"""
src/forecasting.py
Demand Forecasting Engine for Project FORESIGHT.

Features:
- Time-series feature engineering (multi-lags, rolling averages, calendar encodings)
- Temporal train/test split (no lookahead bias)
- Multi-model benchmarking: Naive Baseline, Ridge Regression, RandomForest, HistGradientBoosting
- Evaluation on MAE, RMSE, WAPE, and R2
- 30-day forward recursive multi-step forecasting for all 50 SKUs
- Serialization of models, forecasts, and metric reports
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ForecastingEngine")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
MODELS_DIR = BASE_DIR / "models"


def calculate_wape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Weighted Absolute Percentage Error (WAPE)."""
    sum_actual = np.sum(actual)
    if sum_actual == 0:
        return 0.0
    return float((np.sum(np.abs(actual - predicted)) / sum_actual) * 100)


def load_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load fact sales, calendar, and SKU dimension tables."""
    sales_path = PROCESSED_DIR / "fact_sales_daily.csv"
    cal_path = RAW_DIR / "calendar.csv"
    sku_path = PROCESSED_DIR / "dim_sku.csv"

    if not sales_path.exists():
        raise FileNotFoundError(f"Missing {sales_path}. Run data_pipeline.py first.")

    sales = pd.read_csv(sales_path, parse_dates=["Date"])
    calendar = pd.read_csv(cal_path, parse_dates=["date"])
    sku = pd.read_csv(sku_path)

    logger.info(f"Loaded fact_sales: {sales.shape}, calendar: {calendar.shape}, dim_sku: {sku.shape}")
    return sales, calendar, sku


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Generate time-series lags, rolling window aggregations, and calendar indicators."""
    logger.info("Engineering time-series lag and rolling statistics...")
    data = df.sort_values(["SKU", "Date"]).reset_index(drop=True)

    # Autoregressive Lag Features
    for lag in [7, 14, 21, 28]:
        data[f"lag_{lag}"] = data.groupby("SKU")["Units_Sold"].shift(lag)

    # Moving Window Statistics (shift(1) prevents lookahead bias)
    for window in [7, 14, 28]:
        data[f"rolling_mean_{window}"] = data.groupby("SKU")["Units_Sold"].transform(
            lambda s: s.shift(1).rolling(window).mean()
        )
        data[f"rolling_std_{window}"] = data.groupby("SKU")["Units_Sold"].transform(
            lambda s: s.shift(1).rolling(window).std()
        )

    # Min/Max volatility
    data["rolling_min_7"] = data.groupby("SKU")["Units_Sold"].transform(
        lambda s: s.shift(1).rolling(7).min()
    )
    data["rolling_max_7"] = data.groupby("SKU")["Units_Sold"].transform(
        lambda s: s.shift(1).rolling(7).max()
    )

    # Calendar and Seasonality Signals
    data["day_of_week_num"] = data["Date"].dt.dayofweek
    data["day_of_month"] = data["Date"].dt.day
    data["month"] = data["Date"].dt.month
    data["is_weekend"] = data["day_of_week_num"].isin([5, 6]).astype(int)

    # Cyclical Calendar Transformations
    data["sin_day_of_week"] = np.sin(2 * np.pi * data["day_of_week_num"] / 7)
    data["cos_day_of_week"] = np.cos(2 * np.pi * data["day_of_week_num"] / 7)
    data["sin_month"] = np.sin(2 * np.pi * data["month"] / 12)
    data["cos_month"] = np.cos(2 * np.pi * data["month"] / 12)

    # Clean fillna for rolling std and lags
    data = data.dropna(subset=["lag_28", "rolling_mean_28"]).copy()
    data["rolling_std_7"] = data["rolling_std_7"].fillna(0)
    data["rolling_std_14"] = data["rolling_std_14"].fillna(0)
    data["rolling_std_28"] = data["rolling_std_28"].fillna(0)

    # Categorical Type Encodings
    data["SKU_cat"] = data["SKU"].astype("category")
    data["Category_cat"] = data["Category"].astype("category")
    data["Subcategory_cat"] = data["Subcategory"].astype("category")

    feature_cols = [
        "lag_7", "lag_14", "lag_21", "lag_28",
        "rolling_mean_7", "rolling_std_7",
        "rolling_mean_14", "rolling_std_14",
        "rolling_mean_28", "rolling_std_28",
        "rolling_min_7", "rolling_max_7",
        "day_of_week_num", "day_of_month", "month", "is_weekend",
        "sin_day_of_week", "cos_day_of_week", "sin_month", "cos_month",
        "Promotion", "is_holiday", "Selling_Price", "Cost_Price",
        "SKU_cat", "Category_cat", "Subcategory_cat"
    ]
    categorical_cols = ["SKU_cat", "Category_cat", "Subcategory_cat"]

    logger.info(f"Feature engineering completed: {data.shape[0]} valid rows, {len(feature_cols)} features.")
    return data, feature_cols, categorical_cols


def train_and_benchmark(
    df_feat: pd.DataFrame,
    features: List[str],
    cat_features: List[str],
    test_days: int = 60
) -> Tuple[Dict[str, Dict[str, float]], HistGradientBoostingRegressor, pd.DataFrame]:
    """Perform temporal train/test split and benchmark multiple forecasting models."""
    test_cutoff = df_feat["Date"].max() - pd.Timedelta(days=test_days)
    train_df = df_feat[df_feat["Date"] < test_cutoff]
    test_df = df_feat[df_feat["Date"] >= test_cutoff].copy()

    logger.info(f"Temporal Split -> Train: {train_df['Date'].min():%Y-%m-%d} to {train_df['Date'].max():%Y-%m-%d} ({len(train_df)} rows)")
    logger.info(f"Temporal Split -> Test:  {test_df['Date'].min():%Y-%m-%d} to {test_df['Date'].max():%Y-%m-%d} ({len(test_df)} rows)")

    y_train = train_df["Units_Sold"]
    y_test = test_df["Units_Sold"]
    actuals = y_test.values

    results = {}

    # 1. Baseline Model: 7-Day Moving Average
    baseline_preds = test_df["rolling_mean_7"].values
    results["7-Day Moving Avg (Baseline)"] = {
        "MAE": round(float(mean_absolute_error(actuals, baseline_preds)), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(actuals, baseline_preds))), 3),
        "WAPE (%)": round(calculate_wape(actuals, baseline_preds), 2),
        "R2": round(float(r2_score(actuals, baseline_preds)), 3)
    }

    # Prepare numeric-only features for Ridge / RandomForest
    num_features = [f for f in features if f not in cat_features]
    X_train_num = train_df[num_features]
    X_test_num = test_df[num_features]

    # 2. Ridge Regression
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train_num, y_train)
    ridge_preds = np.clip(ridge.predict(X_test_num), 0, None)
    results["Ridge Regression"] = {
        "MAE": round(float(mean_absolute_error(actuals, ridge_preds)), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(actuals, ridge_preds))), 3),
        "WAPE (%)": round(calculate_wape(actuals, ridge_preds), 2),
        "R2": round(float(r2_score(actuals, ridge_preds)), 3)
    }

    # 3. Random Forest Regressor
    rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train_num, y_train)
    rf_preds = np.clip(rf.predict(X_test_num), 0, None)
    results["Random Forest"] = {
        "MAE": round(float(mean_absolute_error(actuals, rf_preds)), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(actuals, rf_preds))), 3),
        "WAPE (%)": round(calculate_wape(actuals, rf_preds), 2),
        "R2": round(float(r2_score(actuals, rf_preds)), 3)
    }

    # 4. HistGradientBoostingRegressor (Primary Model)
    hgb = HistGradientBoostingRegressor(
        categorical_features=cat_features,
        learning_rate=0.08,
        max_iter=250,
        min_samples_leaf=20,
        random_state=42
    )
    hgb.fit(train_df[features], y_train)
    hgb_preds = np.clip(hgb.predict(test_df[features]), 0, None)
    results["HistGradientBoosting (Best)"] = {
        "MAE": round(float(mean_absolute_error(actuals, hgb_preds)), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(actuals, hgb_preds))), 3),
        "WAPE (%)": round(calculate_wape(actuals, hgb_preds), 2),
        "R2": round(float(r2_score(actuals, hgb_preds)), 3)
    }

    test_df["Predicted_Units"] = hgb_preds
    test_df["Residual"] = test_df["Units_Sold"] - test_df["Predicted_Units"]

    logger.info("Model benchmarking results:")
    for model_name, metrics in results.items():
        logger.info(f" - {model_name:30}: MAE={metrics['MAE']:.3f}, RMSE={metrics['RMSE']:.3f}, WAPE={metrics['WAPE (%)']:.2f}%, R2={metrics['R2']:.3f}")

    return results, hgb, test_df


def generate_30day_forecast(
    model: HistGradientBoostingRegressor,
    sales_df: pd.DataFrame,
    cal_df: pd.DataFrame,
    sku_df: pd.DataFrame,
    features: List[str],
    horizon: int = 30
) -> pd.DataFrame:
    """Generate forward 30-day SKU-level demand forecast recursively."""
    logger.info(f"Generating recursive forward {horizon}-day forecast for all 50 SKUs...")
    max_date = sales_df["Date"].max()
    future_dates = pd.date_range(start=max_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    # Clean calendar for future dates
    cal_lookup = cal_df.copy()
    cal_lookup["date"] = pd.to_datetime(cal_lookup["date"])
    cal_lookup["is_holiday"] = cal_lookup["holiday"].notna().astype(int)
    cal_lookup["Promotion"] = (cal_lookup["promotion_event"].fillna("None") != "None").astype(int)
    cal_map = cal_lookup.set_index("date")

    # Maintain recent sales history per SKU
    sku_metadata = sku_df.set_index("SKU")
    skus = sorted(sales_df["SKU"].unique())

    # Build initial sales history series for fast lag calculation
    history_dict = {
        sku: sales_df[sales_df["SKU"] == sku].sort_values("Date")[["Date", "Units_Sold"]].copy()
        for sku in skus
    }

    forecast_records = []

    for curr_date in future_dates:
        dow = curr_date.dayofweek
        dom = curr_date.day
        month = curr_date.month
        is_wknd = int(dow in [5, 6])
        sin_dow = np.sin(2 * np.pi * dow / 7)
        cos_dow = np.cos(2 * np.pi * dow / 7)
        sin_mon = np.sin(2 * np.pi * month / 12)
        cos_mon = np.cos(2 * np.pi * month / 12)

        # Lookup holiday and promo
        if curr_date in cal_map.index:
            is_hol = int(cal_map.loc[curr_date, "is_holiday"])
            is_prm = int(cal_map.loc[curr_date, "Promotion"])
        else:
            is_hol = 0
            is_prm = 0

        step_rows = []
        for sku in skus:
            h = history_dict[sku]
            recent_sales = h["Units_Sold"].values

            lag_7 = recent_sales[-7] if len(recent_sales) >= 7 else recent_sales[-1]
            lag_14 = recent_sales[-14] if len(recent_sales) >= 14 else recent_sales[-1]
            lag_21 = recent_sales[-21] if len(recent_sales) >= 21 else recent_sales[-1]
            lag_28 = recent_sales[-28] if len(recent_sales) >= 28 else recent_sales[-1]

            roll_7 = recent_sales[-7:]
            roll_14 = recent_sales[-14:]
            roll_28 = recent_sales[-28:]

            meta = sku_metadata.loc[sku]
            price = meta["Selling_Price"]
            cost = meta["Cost_Price"]
            cat = meta["Category"]
            subcat = meta["Subcategory"]

            row = {
                "lag_7": lag_7,
                "lag_14": lag_14,
                "lag_21": lag_21,
                "lag_28": lag_28,
                "rolling_mean_7": float(np.mean(roll_7)),
                "rolling_std_7": float(np.std(roll_7)),
                "rolling_mean_14": float(np.mean(roll_14)),
                "rolling_std_14": float(np.std(roll_14)),
                "rolling_mean_28": float(np.mean(roll_28)),
                "rolling_std_28": float(np.std(roll_28)),
                "rolling_min_7": float(np.min(roll_7)),
                "rolling_max_7": float(np.max(roll_7)),
                "day_of_week_num": dow,
                "day_of_month": dom,
                "month": month,
                "is_weekend": is_wknd,
                "sin_day_of_week": sin_dow,
                "cos_day_of_week": cos_dow,
                "sin_month": sin_mon,
                "cos_month": cos_mon,
                "Promotion": is_prm,
                "is_holiday": is_hol,
                "Selling_Price": price,
                "Cost_Price": cost,
                "SKU_cat": sku,
                "Category_cat": cat,
                "Subcategory_cat": subcat,
                "_SKU": sku,
                "_Date": curr_date
            }
            step_rows.append(row)

        step_df = pd.DataFrame(step_rows)
        # Predict for current step
        preds = np.clip(model.predict(step_df[features]), 0, None)
        step_df["Forecast_Units"] = np.round(preds, 2)
        step_df["Forecast_Revenue"] = np.round(step_df["Forecast_Units"] * step_df["Selling_Price"], 2)

        for _, r in step_df.iterrows():
            sku = r["_SKU"]
            f_units = r["Forecast_Units"]
            # Append predicted value into history to inform next step's lags/rolling stats
            history_dict[sku] = pd.concat([
                history_dict[sku],
                pd.DataFrame([{"Date": curr_date, "Units_Sold": f_units}])
            ], ignore_index=True)

            forecast_records.append({
                "Date": curr_date.strftime("%Y-%m-%d"),
                "SKU": sku,
                "Category": r["Category_cat"],
                "Subcategory": r["Subcategory_cat"],
                "Forecast_Units": f_units,
                "Forecast_Revenue": r["Forecast_Revenue"],
                "Promotion": r["Promotion"],
                "is_holiday": r["is_holiday"]
            })

    forecast_df = pd.DataFrame(forecast_records)
    logger.info(f"Generated {len(forecast_df)} forecast rows ({len(skus)} SKUs x {horizon} days).")
    return forecast_df


def save_artifacts(
    model: HistGradientBoostingRegressor,
    metrics: Dict[str, Dict[str, float]],
    forecast_df: pd.DataFrame,
    test_eval_df: pd.DataFrame
) -> None:
    """Serialize trained model, metric tables, and forecast outputs."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Save Model
    model_path = MODELS_DIR / "demand_forecaster.joblib"
    joblib.dump(model, model_path)
    logger.info(f"Model saved to: {model_path}")

    # 2. Save Metrics JSON and CSV
    metrics_json_path = MODELS_DIR / "forecasting_metrics.json"
    with open(metrics_json_path, "w") as f:
        json.dump(metrics, f, indent=2)

    metrics_csv_path = PROCESSED_DIR / "model_evaluation_metrics.csv"
    pd.DataFrame.from_dict(metrics, orient="index").reset_index().rename(
        columns={"index": "Model"}
    ).to_csv(metrics_csv_path, index=False)
    logger.info(f"Metrics saved to: {metrics_csv_path}")

    # 3. Save 30-Day Forward Forecast
    forecast_path = PROCESSED_DIR / "forecast_demand_30d.csv"
    forecast_df.to_csv(forecast_path, index=False)
    logger.info(f"Forecast saved to: {forecast_path}")

    # 4. Save Out-of-Sample Test Evaluation Dataset for Plots
    test_eval_path = PROCESSED_DIR / "test_evaluation_results.csv"
    cols_to_save = ["Date", "SKU", "Category", "Units_Sold", "Predicted_Units", "Residual"]
    test_eval_df[cols_to_save].to_csv(test_eval_path, index=False)
    logger.info(f"Test evaluation results saved to: {test_eval_path}")


def main():
    logger.info("=== Starting Project FORESIGHT Demand Forecasting Pipeline ===")
    sales, calendar, sku = load_datasets()
    df_feat, features, cat_features = engineer_features(sales)
    metrics, best_model, test_eval = train_and_benchmark(df_feat, features, cat_features, test_days=60)
    forecast_df = generate_30day_forecast(best_model, sales, calendar, sku, features, horizon=30)
    save_artifacts(best_model, metrics, forecast_df, test_eval)
    logger.info("=== Demand Forecasting Pipeline Completed Successfully ===")


if __name__ == "__main__":
    main()
