from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="FORESIGHT | Demand & Inventory Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 12px;
        padding: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_csv(filename, **kwargs):
    candidates = [
        ROOT / "data" / "processed" / filename,
        ROOT / "data" / "Processed" / filename,
    ]
    for path in candidates:
        if path.exists():
            return pd.read_csv(path, **kwargs)
    raise FileNotFoundError(filename)

@st.cache_data
def load_data():
    forecast = load_csv("forecast_demand_30d.csv", parse_dates=["Date"])
    inventory = load_csv("fact_inventory.csv", parse_dates=["Snapshot_Date"])

    risk = None
    for name in ["inventory_risk_optimization.csv", "risk_scores.csv"]:
        try:
            risk = load_csv(name)
            break
        except FileNotFoundError:
            pass

    if risk is None:
        raise FileNotFoundError(
            "Could not find inventory_risk_optimization.csv or risk_scores.csv."
        )

    return forecast, inventory, risk

try:
    forecast, inventory, risk = load_data()
except FileNotFoundError as exc:
    st.error("Required project data is missing.")
    st.code(str(exc))
    st.info(
        "Make sure the generated CSV files are committed under "
        "data/processed/ in the GitHub repository."
    )
    st.stop()

st.title("FORESIGHT")
st.caption("Demand Forecasting & Inventory Intelligence")

forecast["Date"] = pd.to_datetime(forecast["Date"])
inventory["Snapshot_Date"] = pd.to_datetime(inventory["Snapshot_Date"])

for col in [
    "Current_Stock", "On_Order", "Lead_Time_Days", "Avg_Daily_Demand",
    "Calculated_Safety_Stock", "Calculated_Reorder_Point",
    "Expected_Demand_LeadTime", "Projected_Stock", "Lost_Units",
    "Projected_Lost_Revenue", "Selling_Price"
]:
    if col in risk.columns:
        risk[col] = pd.to_numeric(risk[col], errors="coerce")

st.sidebar.header("Filters")

categories = sorted(risk["Category"].dropna().unique()) if "Category" in risk.columns else []
selected_categories = st.sidebar.multiselect(
    "Category", categories, default=categories
)

statuses = (
    sorted(risk["Stockout_Risk_Status"].dropna().unique())
    if "Stockout_Risk_Status" in risk.columns
    else []
)
selected_statuses = st.sidebar.multiselect(
    "Risk status", statuses, default=statuses
)

filtered_risk = risk.copy()
if selected_categories and "Category" in filtered_risk.columns:
    filtered_risk = filtered_risk[filtered_risk["Category"].isin(selected_categories)]
if selected_statuses and "Stockout_Risk_Status" in filtered_risk.columns:
    filtered_risk = filtered_risk[
        filtered_risk["Stockout_Risk_Status"].isin(selected_statuses)
    ]

critical_count = int(
    (filtered_risk["Stockout_Risk_Status"] == "Critical").sum()
    if "Stockout_Risk_Status" in filtered_risk.columns else 0
)
warning_count = int(
    (filtered_risk["Stockout_Risk_Status"] == "Warning").sum()
    if "Stockout_Risk_Status" in filtered_risk.columns else 0
)
overstock_count = int(
    (filtered_risk["Stockout_Risk_Status"] == "Overstock").sum()
    if "Stockout_Risk_Status" in filtered_risk.columns else 0
)
lost_revenue = float(
    filtered_risk["Projected_Lost_Revenue"].sum()
    if "Projected_Lost_Revenue" in filtered_risk.columns else 0
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("SKUs", f"{len(filtered_risk):,}")
c2.metric("Critical", f"{critical_count:,}")
c3.metric("Warning", f"{warning_count:,}")
c4.metric("Overstock", f"{overstock_count:,}")
c5.metric("Projected Lost Revenue", f"₹{lost_revenue:,.0f}")

st.divider()

tab1, tab2, tab3 = st.tabs(
    ["📊 Executive Overview", "📈 Demand Forecast", "📦 SKU Intelligence"]
)

with tab1:
    left, right = st.columns(2)

    with left:
        st.subheader("Inventory Risk Distribution")
        if "Stockout_Risk_Status" in filtered_risk.columns:
            counts = filtered_risk["Stockout_Risk_Status"].value_counts()
            st.bar_chart(counts)

    with right:
        st.subheader("Projected Stock vs Reorder Point")
        if {"Projected_Stock", "Calculated_Reorder_Point"}.issubset(filtered_risk.columns):
            chart_df = filtered_risk.set_index("SKU")[
                ["Projected_Stock", "Calculated_Reorder_Point"]
            ].sort_values("Projected_Stock")
            st.bar_chart(chart_df)

    st.subheader("Priority Inventory Risks")
    priority_cols = [
        "SKU", "Product_Name", "Category", "Current_Stock", "On_Order",
        "Lead_Time_Days", "Projected_Stock", "Calculated_Reorder_Point",
        "Stockout_Risk_Status", "Projected_Lost_Revenue"
    ]
    priority_cols = [c for c in priority_cols if c in filtered_risk.columns]
    priority = filtered_risk.sort_values(
        "Projected_Lost_Revenue", ascending=False
    ).head(10)
    st.dataframe(priority[priority_cols], use_container_width=True, hide_index=True)

with tab2:
    st.subheader("30-Day Demand Forecast")

    forecast_skus = sorted(forecast["SKU"].dropna().unique())
    selected_sku = st.selectbox("Select SKU", forecast_skus)

    sku_forecast = (
        forecast[forecast["SKU"] == selected_sku]
        .sort_values("Date")
        .set_index("Date")
    )

    if "Forecast_Units" in sku_forecast.columns:
        st.line_chart(sku_forecast["Forecast_Units"])

    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("30-Day Forecast Units", f"{sku_forecast['Forecast_Units'].sum():,.0f}")
    fc2.metric("Average Daily Forecast", f"{sku_forecast['Forecast_Units'].mean():,.1f}")
    if "Forecast_Revenue" in sku_forecast.columns:
        fc3.metric("Forecast Revenue", f"₹{sku_forecast['Forecast_Revenue'].sum():,.0f}")

    display_cols = [
        c for c in
        ["Date", "SKU", "Category", "Subcategory", "Forecast_Units", "Forecast_Revenue"]
        if c in sku_forecast.reset_index().columns
    ]
    st.dataframe(
        sku_forecast.reset_index()[display_cols],
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    st.subheader("SKU-Level Inventory Intelligence")

    sku_options = sorted(filtered_risk["SKU"].dropna().unique())
    if not sku_options:
        st.warning("No SKUs match the selected filters.")
    else:
        detail_sku = st.selectbox("Select SKU", sku_options, key="detail_sku")
        detail = filtered_risk[filtered_risk["SKU"] == detail_sku].iloc[0]

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Current Stock", f"{detail.get('Current_Stock', 0):,.0f}")
        d2.metric("On Order", f"{detail.get('On_Order', 0):,.0f}")
        d3.metric("Lead Time", f"{detail.get('Lead_Time_Days', 0):.0f} days")
        d4.metric("Risk", str(detail.get("Stockout_Risk_Status", "N/A")))

        detail_cols = [
            "SKU", "Product_Name", "Category", "Subcategory",
            "Current_Stock", "On_Order", "Lead_Time_Days",
            "Avg_Daily_Demand", "Demand_Std",
            "Calculated_Safety_Stock", "Calculated_Reorder_Point",
            "Expected_Demand_LeadTime", "Projected_Stock",
            "Stockout_Risk_Status", "Lost_Units", "Projected_Lost_Revenue"
        ]
        detail_cols = [c for c in detail_cols if c in filtered_risk.columns]
        st.dataframe(
            filtered_risk[filtered_risk["SKU"] == detail_sku][detail_cols],
            use_container_width=True,
            hide_index=True,
        )

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    st.caption(
        f"Forecast horizon: {forecast['Date'].min().date()} → "
        f"{forecast['Date'].max().date()}"
    )
with col_b:
    csv = filtered_risk.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered risk report",
        data=csv,
        file_name="foresight_risk_report.csv",
        mime="text/csv",
    )
