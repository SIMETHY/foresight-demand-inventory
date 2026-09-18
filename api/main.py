"""
api/main.py — Project FORESIGHT Scoring Service (D6)

Run from the repo root:
    uvicorn api.main:app --reload

Endpoints:
    GET  /health                      — service status
    GET  /skus                        — list all known SKUs
    GET  /forecast/{sku}?days=30      — on-demand recursive forecast (recomputed from the trained model)
    GET  /forecast                    — pre-generated 30-day forecast for all SKUs (from forecast_demand_30d.csv)
    GET  /risk/{sku}                  — risk score for one SKU (from inventory_risk_optimization.csv)
    GET  /risk?status=...             — full risk table, optionally filtered by Stockout_Risk_Status
"""

from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent  # repo root
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
MODELS_DIR = BASE_DIR / "models"

app = FastAPI(title="FORESIGHT Scoring Service", version="1.0")

# ---------- Load model + data once at startup ----------
model = joblib.load(MODELS_DIR / "demand_forecaster.joblib")
sales = pd.read_csv(PROCESSED_DIR / "fact_sales_daily.csv", parse_dates=["Date"])
sku_meta = pd.read_csv(PROCESSED_DIR / "dim_sku.csv").set_index("SKU")
calendar = pd.read_csv(RAW_DIR / "calendar.csv", parse_dates=["date"])
calendar["is_holiday"] = calendar["holiday"].notna().astype(int)
calendar["Promotion"] = (calendar["promotion_event"].fillna("None") != "None").astype(int)
cal_map = calendar.set_index("date")

risk_scores = pd.read_csv(PROCESSED_DIR / "inventory_risk_optimization.csv")
precomputed_forecast = pd.read_csv(PROCESSED_DIR / "forecast_demand_30d.csv", parse_dates=["Date"])

FEATURES = [
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

ALL_SKUS = sorted(sales["SKU"].unique())


def recursive_forecast_one_sku(sku: str, horizon: int) -> pd.DataFrame:
    """Recursively forecast `horizon` days forward for a single SKU using the trained model."""
    history = sales[sales["SKU"] == sku].sort_values("Date")[["Date", "Units_Sold"]].copy()
    max_date = sales["Date"].max()
    future_dates = pd.date_range(start=max_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    meta = sku_meta.loc[sku]
    price, cost, cat, subcat = meta["Selling_Price"], meta["Cost_Price"], meta["Category"], meta["Subcategory"]

    records = []
    for curr_date in future_dates:
        dow, dom, month = curr_date.dayofweek, curr_date.day, curr_date.month
        is_wknd = int(dow in [5, 6])
        sin_dow, cos_dow = np.sin(2 * np.pi * dow / 7), np.cos(2 * np.pi * dow / 7)
        sin_mon, cos_mon = np.sin(2 * np.pi * month / 12), np.cos(2 * np.pi * month / 12)

        if curr_date in cal_map.index:
            is_hol = int(cal_map.loc[curr_date, "is_holiday"])
            is_prm = int(cal_map.loc[curr_date, "Promotion"])
        else:
            is_hol, is_prm = 0, 0

        recent = history["Units_Sold"].values
        lag_7 = recent[-7] if len(recent) >= 7 else recent[-1]
        lag_14 = recent[-14] if len(recent) >= 14 else recent[-1]
        lag_21 = recent[-21] if len(recent) >= 21 else recent[-1]
        lag_28 = recent[-28] if len(recent) >= 28 else recent[-1]
        roll_7, roll_14, roll_28 = recent[-7:], recent[-14:], recent[-28:]

        row = pd.DataFrame([{
            "lag_7": lag_7, "lag_14": lag_14, "lag_21": lag_21, "lag_28": lag_28,
            "rolling_mean_7": float(np.mean(roll_7)), "rolling_std_7": float(np.std(roll_7)),
            "rolling_mean_14": float(np.mean(roll_14)), "rolling_std_14": float(np.std(roll_14)),
            "rolling_mean_28": float(np.mean(roll_28)), "rolling_std_28": float(np.std(roll_28)),
            "rolling_min_7": float(np.min(roll_7)), "rolling_max_7": float(np.max(roll_7)),
            "day_of_week_num": dow, "day_of_month": dom, "month": month, "is_weekend": is_wknd,
            "sin_day_of_week": sin_dow, "cos_day_of_week": cos_dow,
            "sin_month": sin_mon, "cos_month": cos_mon,
            "Promotion": is_prm, "is_holiday": is_hol,
            "Selling_Price": price, "Cost_Price": cost,
            "SKU_cat": sku, "Category_cat": cat, "Subcategory_cat": subcat,
        }])

        pred = float(np.clip(model.predict(row[FEATURES]), 0, None)[0])
        history = pd.concat([history, pd.DataFrame([{"Date": curr_date, "Units_Sold": pred}])], ignore_index=True)
        records.append({
            "Date": curr_date.strftime("%Y-%m-%d"),
            "SKU": sku,
            "Forecast_Units": round(pred, 2),
            "Forecast_Revenue": round(pred * price, 2),
        })

    return pd.DataFrame(records)


@app.get("/health")
def health():
    return {"status": "ok", "skus_loaded": len(ALL_SKUS), "model": type(model).__name__}


@app.get("/skus")
def list_skus():
    return {"skus": ALL_SKUS}


@app.get("/forecast/{sku}")
def forecast_sku(sku: str, days: int = 30):
    if sku not in ALL_SKUS:
        raise HTTPException(status_code=404, detail=f"Unknown SKU: {sku}")
    if not (1 <= days <= 90):
        raise HTTPException(status_code=400, detail="days must be between 1 and 90")
    result = recursive_forecast_one_sku(sku, days)
    return result.to_dict(orient="records")


@app.get("/forecast")
def forecast_all():
    return precomputed_forecast.assign(
        Date=precomputed_forecast["Date"].dt.strftime("%Y-%m-%d")
    ).to_dict(orient="records")


@app.get("/risk/{sku}")
def risk_sku(sku: str):
    row = risk_scores[risk_scores["SKU"] == sku]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Unknown SKU: {sku}")
    return row.iloc[0].to_dict()


@app.get("/risk")
def risk_all(status: Optional[str] = None):
    df = risk_scores
    if status:
        df = df[df["Stockout_Risk_Status"] == status]
    return df.to_dict(orient="records")