"""
src/risk_scoring.py
Inventory Risk & Safety Stock Optimization Engine for Project FORESIGHT (Milestone 4).

Features:
- Dynamic Safety Stock calculation using historical demand volatility and supplier lead time (Z=1.65 for 95% service level)
- Forward-looking Reorder Point (ROP) driven by machine learning 30-day demand forecasts
- Lead-time forward stock projection (Current Stock + On Order - Forecast Demand over Lead Time)
- 4-Tier Risk Classification: Critical (Stockout Gap), Warning, Normal, Overstock
- Financial Impact Quantification: Projected Lost Revenue for Stockout and Working Capital Tied Up in Overstock
- Actionable Recommendations: Recommended Order Quantity to restore healthy stock levels
- Output serialization to data/processed/inventory_risk_optimization.csv
"""

import argparse
import logging
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("RiskOptimizationEngine")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def load_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load processed daily sales, inventory snapshots, and 30-day forward demand forecast."""
    sales_path = PROCESSED_DIR / "fact_sales_daily.csv"
    inv_path = PROCESSED_DIR / "fact_inventory.csv"
    forecast_path = PROCESSED_DIR / "forecast_demand_30d.csv"

    for p in [sales_path, inv_path, forecast_path]:
        if not p.exists():
            raise FileNotFoundError(f"Missing required dataset: {p}. Ensure M1 and M3 pipelines have been run.")

    sales = pd.read_csv(sales_path, parse_dates=["Date"])
    inv = pd.read_csv(inv_path, parse_dates=["Snapshot_Date"])
    forecast = pd.read_csv(forecast_path, parse_dates=["Date"])

    logger.info(f"Loaded datasets -> sales: {sales.shape}, inv: {inv.shape}, forecast: {forecast.shape}")
    return sales, inv, forecast


def calculate_inventory_risk(
    sales: pd.DataFrame,
    inv: pd.DataFrame,
    forecast: pd.DataFrame,
    service_level_z: float = 1.65,
    target_buffer_multiplier: float = 1.5
) -> pd.DataFrame:
    """
    Compute safety stock, reorder point, projected stock, risk status,
    and financial metrics for all active SKUs.
    """
    latest_date = inv["Snapshot_Date"].max()
    latest_inv = inv[inv["Snapshot_Date"] == latest_date].copy().set_index("SKU")
    logger.info(f"Using latest inventory snapshot from: {latest_date:%Y-%m-%d} ({len(latest_inv)} SKUs)")

    # 1. Historical demand volatility per SKU
    demand_std = sales.groupby("SKU")["Units_Sold"].std()

    # 2. Forward-looking average daily demand from ML forecast
    avg_daily_demand = forecast.groupby("SKU")["Forecast_Units"].mean()

    # 3. Lead time per SKU
    lead_times = latest_inv["Lead_Time_Days"]

    # 4. Dynamic Safety Stock (Z * sigma * sqrt(L))
    calc_safety_stock = (service_level_z * demand_std * np.sqrt(lead_times)).round(0)

    # 5. Dynamic Reorder Point ((avg_daily_demand * L) + Safety_Stock)
    calc_reorder_point = ((avg_daily_demand * lead_times) + calc_safety_stock).round(0)

    # 6. Expected demand over lead time (sum of forward forecast for the first L days)
    expected_demand_lt = {}
    for sku, lt in lead_times.items():
        sku_fc = forecast[forecast["SKU"] == sku].sort_values("Date")
        expected_demand_lt[sku] = sku_fc["Forecast_Units"].head(int(lt)).sum()
    expected_demand_lt = pd.Series(expected_demand_lt)

    # 7. Projected stock position at the end of supplier lead time
    projected_stock = latest_inv["Current_Stock"] + latest_inv["On_Order"] - expected_demand_lt

    # 8. Assemble structured table
    df_risk = pd.DataFrame({
        "SKU": latest_inv.index,
        "Product_Name": latest_inv["Product_Name"],
        "Category": latest_inv["Category"],
        "Subcategory": latest_inv["Subcategory"],
        "Current_Stock": latest_inv["Current_Stock"],
        "On_Order": latest_inv["On_Order"],
        "Lead_Time_Days": lead_times,
        "Avg_Daily_Demand": avg_daily_demand.reindex(latest_inv.index).round(2),
        "Demand_Std": demand_std.reindex(latest_inv.index).round(2),
        "Calculated_Safety_Stock": calc_safety_stock.reindex(latest_inv.index).round(0),
        "Calculated_Reorder_Point": calc_reorder_point.reindex(latest_inv.index).round(0),
        "Expected_Demand_LeadTime": expected_demand_lt.reindex(latest_inv.index).round(2),
        "Projected_Stock": projected_stock.reindex(latest_inv.index).round(2),
        "Selling_Price": latest_inv["Selling_Price"],
        "Cost_Price": latest_inv["Cost_Price"] if "Cost_Price" in latest_inv.columns else 0.0,
    }).reset_index(drop=True)

    # 9. 4-Tier Risk Classification
    def classify(row: pd.Series) -> str:
        if row["Projected_Stock"] < 0:
            return "Critical"
        elif row["Projected_Stock"] <= row["Calculated_Reorder_Point"]:
            return "Warning"
        elif row["Projected_Stock"] > row["Calculated_Reorder_Point"] * 2:
            return "Overstock"
        else:
            return "Normal"

    df_risk["Stockout_Risk_Status"] = df_risk.apply(classify, axis=1)

    # 10. Financial Impact: Stockout Lost Units & Lost Revenue
    df_risk["Lost_Units"] = np.where(
        df_risk["Stockout_Risk_Status"] == "Critical",
        (-df_risk["Projected_Stock"]).round(2),
        0.0
    )
    df_risk["Projected_Lost_Revenue"] = np.where(
        df_risk["Stockout_Risk_Status"] == "Critical",
        (df_risk["Lost_Units"] * df_risk["Selling_Price"]).round(2),
        0.0
    )

    # 11. Overstock Impact: Excess Units & Tied-up Working Capital
    df_risk["Excess_Units"] = np.where(
        df_risk["Stockout_Risk_Status"] == "Overstock",
        np.maximum(0, (df_risk["Projected_Stock"] - (df_risk["Calculated_Reorder_Point"] * 2))).round(2),
        0.0
    )
    df_risk["Tied_Up_Capital"] = np.where(
        df_risk["Stockout_Risk_Status"] == "Overstock",
        (df_risk["Excess_Units"] * df_risk["Cost_Price"]).round(2),
        0.0
    )

    # 12. Actionable Recommendation: Recommended Order Quantity
    # For Critical & Warning SKUs: Order up to target level (ROP * target_buffer_multiplier)
    target_inventory = df_risk["Calculated_Reorder_Point"] * target_buffer_multiplier
    needed_qty = target_inventory - df_risk["Projected_Stock"]
    df_risk["Recommended_Order_Qty"] = np.where(
        df_risk["Stockout_Risk_Status"].isin(["Critical", "Warning"]),
        np.maximum(0, np.ceil(needed_qty)).astype(int),
        0
    )

    return df_risk


def save_and_report(df_risk: pd.DataFrame, output_file: Path) -> None:
    """Save risk evaluation table and log executive summary."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_risk.to_csv(output_file, index=False)
    logger.info(f"Inventory risk report saved to: {output_file} (Shape: {df_risk.shape})")

    # Executive Summary Logging
    status_counts = df_risk["Stockout_Risk_Status"].value_counts().to_dict()
    total_lost_rev = df_risk["Projected_Lost_Revenue"].sum()
    total_tied_up = df_risk["Tied_Up_Capital"].sum()
    critical_skus = df_risk[df_risk["Stockout_Risk_Status"] == "Critical"][["SKU", "Product_Name", "Projected_Lost_Revenue", "Recommended_Order_Qty"]]

    logger.info("=== Inventory Risk Optimization Summary ===")
    logger.info(f"Distribution: {status_counts}")
    logger.info(f"Total Projected Lost Revenue (Critical Stockout): ₹{total_lost_rev:,.2f}")
    logger.info(f"Total Working Capital Tied Up (Overstock):         ₹{total_tied_up:,.2f}")
    logger.info("Critical SKUs Needing Immediate Replenishment:")
    for _, row in critical_skus.iterrows():
        logger.info(f" - {row['SKU']} ({row['Product_Name']}): Lost Rev = ₹{row['Projected_Lost_Revenue']:,.2f}, Recommended Reorder = {row['Recommended_Order_Qty']} units")


def main():
    parser = argparse.ArgumentParser(description="FORESIGHT Inventory Risk & Safety Stock Engine")
    parser.add_argument("--service-level-z", type=float, default=1.65, help="Z-score for service level (1.65=95%, 2.33=99%)")
    parser.add_argument("--buffer-multiplier", type=float, default=1.5, help="Target inventory buffer multiplier")
    args = parser.parse_args()

    logger.info("=== Running Project FORESIGHT Milestone 4: Inventory Risk Engine ===")
    sales, inv, forecast = load_datasets()
    df_risk = calculate_inventory_risk(
        sales=sales,
        inv=inv,
        forecast=forecast,
        service_level_z=args.service_level_z,
        target_buffer_multiplier=args.buffer_multiplier
    )
    output_path = PROCESSED_DIR / "inventory_risk_optimization.csv"
    save_and_report(df_risk, output_path)
    logger.info("=== Milestone 4 Engine Completed Successfully ===")


if __name__ == "__main__":
    main()
