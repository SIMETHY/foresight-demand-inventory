"""
FORESIGHT — Planning Dashboard (D5)
Run with: streamlit run dashboards/app.py   (run from the ForeSight/ repo root)
"""

import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # repo root
DATA_DIR = BASE_DIR / "data" / "processed"

st.set_page_config(page_title="FORESIGHT — Planning Dashboard", layout="wide")

# ---------- Load ----------
@st.cache_data
def load_data():
    sales = pd.read_csv(DATA_DIR / "fact_sales_daily.csv", parse_dates=["Date"])
    risk = pd.read_csv(DATA_DIR / "risk_scores.csv")
    forecast = pd.read_csv(DATA_DIR / "forecast_demand_30d.csv", parse_dates=["Date"])
    return sales, risk, forecast

sales, risk, forecast = load_data()

st.title("📦 FORESIGHT — Planning Dashboard")
st.caption("Demand forecast & inventory risk overview — NorthBay Living")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
categories = sorted(sales["Category"].dropna().unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

date_min, date_max = sales["Date"].min(), sales["Date"].max()
date_range = st.sidebar.date_input("Date range", (date_min, date_max), min_value=date_min, max_value=date_max)

skus = sorted(sales.loc[sales["Category"].isin(selected_categories), "SKU"].unique())
selected_skus = st.sidebar.multiselect("SKU (optional)", skus, default=[])

# ---------- Apply filters ----------
mask = sales["Category"].isin(selected_categories)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask &= sales["Date"].between(start, end)
if selected_skus:
    mask &= sales["SKU"].isin(selected_skus)

f_sales = sales[mask]
f_risk = risk[risk["Category"].isin(selected_categories) & (risk["SKU"].isin(selected_skus) if selected_skus else True)]
f_forecast = forecast[forecast["Category"].isin(selected_categories) & (forecast["SKU"].isin(selected_skus) if selected_skus else True)]

# ---------- KPI row ----------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Units Sold", f"{f_sales['Units_Sold'].sum():,.0f}")
c2.metric("Total Revenue", f"₹{f_sales['Revenue'].sum():,.0f}")
neg_margin_pct = (f_sales["Gross_Margin_Per_Unit"] < 0).mean() * 100
c3.metric("Negative-Margin Sales", f"{neg_margin_pct:.1f}%")
stockout_count = (f_risk["Risk_Tier"] == "High Risk - Stockout").sum()
c4.metric("SKUs at Stockout Risk", f"{stockout_count}")
c5.metric("Forecasted Units (30d)", f"{f_forecast['Forecast_Units'].sum():,.0f}")

st.divider()

# ---------- Tabs ----------
tab_trend, tab_forecast, tab_season, tab_category, tab_margin, tab_risk = st.tabs(
    ["📈 Sales Trend", "🔮 Forecast", "📅 Seasonality", "🏷️ Category / SKU", "⚠️ Margin", "📦 Risk"]
)

# --- Sales Trend ---
with tab_trend:
    granularity = st.radio("Granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)
    ts = f_sales.copy()
    if granularity == "Daily":
        grouped = ts.groupby("Date")["Units_Sold"].sum().reset_index()
    elif granularity == "Weekly":
        grouped = ts.groupby(ts["Date"].dt.to_period("W").dt.start_time)["Units_Sold"].sum().reset_index()
    else:
        grouped = ts.groupby(ts["Date"].dt.to_period("M").dt.start_time)["Units_Sold"].sum().reset_index()
    fig = px.line(grouped, x="Date", y="Units_Sold", title=f"{granularity} Units Sold")
    st.plotly_chart(fig, use_container_width=True)

    fig_rev = px.line(
        ts.groupby(ts["Date"].dt.to_period("M").dt.start_time)["Revenue"].sum().reset_index(),
        x="Date", y="Revenue", title="Monthly Revenue"
    )
    st.plotly_chart(fig_rev, use_container_width=True)

# --- Forecast (NEW — uses real model output) ---
with tab_forecast:
    st.caption(f"30-day forward forecast: {forecast['Date'].min().date()} to {forecast['Date'].max().date()}")

    daily_forecast = f_forecast.groupby("Date")["Forecast_Units"].sum().reset_index()
    fig = px.line(daily_forecast, x="Date", y="Forecast_Units", title="Forecasted Units Sold — Next 30 Days")
    st.plotly_chart(fig, use_container_width=True)

    if selected_skus:
        sku_fc = f_forecast[f_forecast["SKU"].isin(selected_skus)]
        fig2 = px.line(sku_fc, x="Date", y="Forecast_Units", color="SKU", title="Forecast by Selected SKU")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        top_forecast_skus = (
            f_forecast.groupby("SKU")["Forecast_Units"].sum().sort_values(ascending=False).head(10).reset_index()
        )
        fig2 = px.bar(top_forecast_skus, x="SKU", y="Forecast_Units", title="Top 10 SKUs by Forecasted Demand (30d)")
        st.plotly_chart(fig2, use_container_width=True)

# --- Seasonality ---
with tab_season:
    col1, col2 = st.columns(2)
    with col1:
        holiday_avg = f_sales.groupby("is_holiday")["Units_Sold"].mean().reset_index()
        holiday_avg["is_holiday"] = holiday_avg["is_holiday"].map({0: "Non-Holiday", 1: "Holiday"})
        fig = px.bar(holiday_avg, x="is_holiday", y="Units_Sold", title="Avg Units Sold — Holiday vs Non-Holiday")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        promo_avg = f_sales.groupby("promotion_event")["Units_Sold"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(promo_avg, x="promotion_event", y="Units_Sold", title="Avg Units Sold by Promotion Type")
        st.plotly_chart(fig, use_container_width=True)

    month_avg = f_sales.groupby(f_sales["Date"].dt.month)["Units_Sold"].sum().reset_index()
    month_avg.columns = ["Month", "Units_Sold"]
    fig = px.bar(month_avg, x="Month", y="Units_Sold", title="Total Units Sold by Calendar Month (seasonality)")
    st.plotly_chart(fig, use_container_width=True)

# --- Category / SKU ---
with tab_category:
    col1, col2 = st.columns(2)
    with col1:
        cat_rev = f_sales.groupby("Category")["Revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(cat_rev, x="Category", y="Revenue", title="Revenue by Category")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        top_skus = f_sales.groupby("SKU")["Units_Sold"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(top_skus, x="SKU", y="Units_Sold", title="Top 10 SKUs by Units Sold")
        st.plotly_chart(fig, use_container_width=True)

    bottom_skus = f_sales.groupby("SKU")["Units_Sold"].sum().sort_values().head(10).reset_index()
    fig = px.bar(bottom_skus, x="SKU", y="Units_Sold", title="Bottom 10 SKUs by Units Sold (slow movers)")
    st.plotly_chart(fig, use_container_width=True)

# --- Margin ---
with tab_margin:
    st.warning(
        f"{neg_margin_pct:.1f}% of sales in the current view have negative gross margin. "
        "Flagged for review — not automatically treated as an error."
    )
    cat_margin = (
        f_sales.groupby("Category")["Gross_Margin_Per_Unit"]
        .apply(lambda x: (x < 0).mean() * 100)
        .sort_values(ascending=False)
        .reset_index(name="Negative_Margin_Pct")
    )
    fig = px.bar(cat_margin, x="Category", y="Negative_Margin_Pct", title="Negative-Margin Sale Rate by Category (%)")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(f_sales, x="Gross_Margin_Per_Unit", nbins=50, title="Gross Margin per Unit — Distribution")
    st.plotly_chart(fig2, use_container_width=True)

# --- Risk (NEW — uses real risk_scores.csv, replaces old placeholder rule) ---
with tab_risk:
    risk_counts = f_risk["Risk_Tier"].value_counts().reset_index()
    risk_counts.columns = ["Risk_Tier", "Count"]
    fig = px.bar(risk_counts, x="Risk_Tier", y="Count", title="SKUs by Risk Tier (forecast-driven)")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        f_risk.sort_values("Days_Of_Stock_Remaining").head(15),
        x="SKU", y="Days_Of_Stock_Remaining", color="Risk_Tier",
        title="Lowest Days-of-Stock-Remaining (top 15 most urgent)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        f_risk[["SKU", "Product_Name", "Category", "Current_Stock", "On_Order",
                "Expected_Demand_LeadTime", "Projected_Stock", "Safety_Stock",
                "Reorder_Point", "Days_Of_Stock_Remaining", "Risk_Tier"]]
        .sort_values("Days_Of_Stock_Remaining"),
        use_container_width=True, hide_index=True
    )

    st.caption(
        "Risk tiers are forecast-driven: Projected_Stock = Current_Stock + On_Order − "
        "expected demand over each SKU's lead time (from the trained demand model)."
    )