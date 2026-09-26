import streamlit as st
import requests
import pandas as pd
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Foresight Dashboard",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* =====================================================
       FORESIGHT COLOR THEME
       Purple + Teal + Cyan + Coral
       ===================================================== */

    .stApp {
        background: linear-gradient(180deg, #fbf9ff 0%, #f7f9fc 48%, #f5f8fb 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #25213a;
        letter-spacing: -0.7px;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 15px;
        color: #77728a;
        margin-bottom: 28px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: #25213a;
        margin-top: 30px;
        margin-bottom: 16px;
        letter-spacing: -0.2px;
    }

    /* =====================================================
       KPI CARDS
       ===================================================== */

    .kpi-card {
        background: rgba(255,255,255,0.96);
        padding: 19px 20px;
        border-radius: 15px;
        border: 1px solid #ebe7f4;
        box-shadow: 0 5px 18px rgba(49, 36, 75, 0.06);
        min-height: 112px;
        transition: transform .15s ease, box-shadow .15s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 9px 24px rgba(49, 36, 75, 0.10);
    }

    .kpi-title {
        font-size: 13px;
        color: #77728a;
        font-weight: 650;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 29px;
        font-weight: 800;
        color: #25213a;
        letter-spacing: -0.4px;
    }

    .kpi-critical { border-left: 6px solid #ef6f73; }
    .kpi-warning { border-left: 6px solid #fe9496; }
    .kpi-normal { border-left: 6px solid #1bcfb4; }
    .kpi-overstock { border-left: 6px solid #4bcbeb; }
    .kpi-blue { border-left: 6px solid #4bcbeb; }
    .kpi-teal { border-left: 6px solid #1bcfb4; }
    .kpi-purple { border-left: 6px solid #a05aff; }
    .kpi-revenue { border-left: 6px solid #9e58ff; }

    /* =====================================================
       GENERAL STREAMLIT ELEMENTS
       ===================================================== */

    .stApp,
    .stApp p,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stMetricValue"],
    .stApp [data-testid="stMetricDelta"] {
        color: #25213a !important;
    }

    .stMetric {
        background: rgba(255,255,255,0.94);
        border: 1px solid #ebe7f4;
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 4px 15px rgba(49, 36, 75, 0.045);
    }

    .stMetric label {
        color: #77728a !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: #25213a !important;
        font-weight: 800;
    }

    /* Inputs */
    .stApp [data-baseweb="select"] > div {
        border-radius: 10px;
        border-color: #ddd7eb;
    }

    .stApp [data-baseweb="select"]:focus-within > div {
        border-color: #a05aff;
        box-shadow: 0 0 0 1px #a05aff;
    }

    /* Expanders */
    .stApp [data-testid="stExpander"] {
        border: 1px solid #e7e1f0;
        border-radius: 13px;
        background: rgba(255,255,255,0.72);
        overflow: hidden;
    }

    /* Alerts */
    .stApp [data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid #e8e2f0;
    }

    /* Dataframes */
    .stApp [data-testid="stDataFrame"] {
        border: 2px solid #d8cbea;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 5px 18px rgba(49, 36, 75, 0.07);
        background: #ffffff;
    }

    /* =====================================================
       SIDEBAR
       ===================================================== */

    .stApp [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #241d35 0%, #302346 58%, #382653 100%);
        border-right: 1px solid #4a3567;
    }

    .stApp [data-testid="stSidebar"],
    .stApp [data-testid="stSidebar"] p,
    .stApp [data-testid="stSidebar"] label,
    .stApp [data-testid="stSidebar"] span,
    .stApp [data-testid="stSidebar"] div,
    .stApp [data-testid="stSidebar"] small,
    .stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    .stApp [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.14);
    }

    .stApp [data-testid="stSidebar"] [data-baseweb="select"],
    .stApp [data-testid="stSidebar"] [data-baseweb="select"] *,
    .stApp [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    [data-baseweb="popover"] [role="option"],
    [data-baseweb="popover"] [role="option"] *,
    [data-baseweb="menu"] [role="option"],
    [data-baseweb="menu"] [role="option"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="menu"] [role="option"]:hover {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: #49325f !important;
    }

    .stApp [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 10px;
        padding: 6px 9px;
        margin: 2px 0;
        transition: background .15s ease;
    }

    .stApp [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(160,90,255,0.16);
    }

    .stApp [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(160,90,255,0.28), rgba(27,207,180,0.12));
        box-shadow: inset 3px 0 0 #a05aff;
    }

    /* Download buttons */
    .stApp [data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #a05aff, #7f45df) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #a05aff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    .stApp [data-testid="stDownloadButton"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    .stApp [data-testid="stDownloadButton"] button:hover {
        background: linear-gradient(90deg, #8e4ff0, #6e3bc9) !important;
        border-color: #8e4ff0 !important;
    }

    /* Primary buttons */
    .stApp button[kind="primary"] {
        background: linear-gradient(90deg, #a05aff, #1bcfb4) !important;
        border: none !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# LIGHT TABLE + CHART STYLING
# =========================================================

TABLE_HEADER = "#F3EEFF"
TABLE_BORDER = "#E7DFF2"
TEXT_DARK = "#25213A"
TEXT_MUTED = "#77728A"
PURPLE = "#A05AFF"
TEAL = "#1BCFB4"
CYAN = "#4BCBEB"
CORAL = "#FE9496"


def table_height(df, max_height=520, min_height=175):
    """Give tables only as much vertical space as their rows need."""
    if df is None:
        return min_height
    rows = len(df)
    # Header + compact row height + a little breathing room.
    return max(min_height, min(max_height, 52 + (rows * 35)))


def style_table(df, theme="lavender"):
    """Style tables with soft Foresight pastel themes without changing their data."""
    if df is None or df.empty:
        return df

    palettes = {
        "lavender": {
            "header": "#DCC4FF", "body": "#F6EFFF", "alt": "#EDE0FF",
            "border": "#C6A7F2", "accent": "#6F35C5",
        },
        "pink": {
            "header": "#FFBFC7", "body": "#FFF0F2", "alt": "#FFE0E5",
            "border": "#F29AA6", "accent": "#C83D54",
        },
        "teal": {
            "header": "#AEEBDD", "body": "#EAF9F5", "alt": "#D7F4ED",
            "border": "#79D7C4", "accent": "#08705E",
        },
        "cyan": {
            "header": "#B8EAF7", "body": "#EAF8FC", "alt": "#D8F2F9",
            "border": "#7DD2E8", "accent": "#086D8D",
        },
        "coral": {
            "header": "#FFC5BD", "body": "#FFF0ED", "alt": "#FFE1DC",
            "border": "#F1A095", "accent": "#A53E12",
        },
    }
    palette = palettes.get(theme, palettes["lavender"])

    styler = (
        df.style
        .set_properties(
            **{
                "background-color": palette["body"],
                "color": TEXT_DARK,
                "border-color": palette["border"],
                "font-size": "13px",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", palette["header"]),
                        ("color", TEXT_DARK),
                        ("font-weight", "700"),
                        ("border-color", palette["border"]),
                    ],
                },
                {
                    "selector": "td",
                    "props": [("border-color", palette["border"])],
                },
                {
                    "selector": "tbody tr:nth-child(even) td",
                    "props": [("background-color", palette["alt"])],
                },
                {
                    "selector": "tbody tr:hover td",
                    "props": [("background-color", palette["header"])],
                },
            ]
        )
    )

    # Keep risk status visually meaningful without changing any table data.
    if "Stockout_Risk_Status" in df.columns:
        def risk_style(value):
            styles = {
                "Critical": "background-color: #FDE2E4; color: #B4232F; font-weight: 700;",
                "Warning": "background-color: #FFF0E6; color: #B54708; font-weight: 700;",
                "Normal": "background-color: #E3F8F3; color: #087F6A; font-weight: 700;",
                "Overstock": "background-color: #E8F6FC; color: #087EA4; font-weight: 700;",
            }
            return styles.get(value, "")

        styler = styler.map(risk_style, subset=["Stockout_Risk_Status"])

    return styler


def style_chart(fig, chart_kind="default"):
    """Apply a light Plotly theme while preserving the chart's existing meaning."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color=TEXT_DARK, size=13),
        title_font=dict(color=TEXT_DARK, size=17),
        legend=dict(
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor=TABLE_BORDER,
            borderwidth=0,
            font=dict(color=TEXT_MUTED),
        ),
        margin=dict(l=55, r=30, t=65, b=55),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=TABLE_BORDER,
        tickfont=dict(color=TEXT_MUTED),
        title_font=dict(color=TEXT_DARK),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EEEAF5",
        zeroline=False,
        linecolor=TABLE_BORDER,
        tickfont=dict(color=TEXT_MUTED),
        title_font=dict(color=TEXT_DARK),
    )

    if chart_kind == "pie":
        fig.update_traces(
            marker=dict(
                colors=[PURPLE, TEAL, CYAN, CORAL, "#9E58FF"],
                line=dict(color="#FFFFFF", width=2),
            )
        )
    elif chart_kind == "area":
        fig.update_traces(
            line=dict(color=CYAN, width=3),
            fillcolor="rgba(75,203,235,0.20)",
        )
    elif chart_kind == "line":
        fig.update_traces(
            line=dict(color=PURPLE, width=3),
            marker=dict(color=PURPLE, size=7),
        )
    elif chart_kind == "grouped_bar":
        colors = [PURPLE, TEAL, CYAN, CORAL]
        for i, trace in enumerate(fig.data):
            trace.marker.color = colors[i % len(colors)]
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 1
    elif chart_kind == "coral_bar":
        fig.update_traces(
            marker_color=CORAL,
            marker_line_color="#FFFFFF",
            marker_line_width=1,
        )
    else:
        fig.update_traces(
            marker_color=PURPLE,
            marker_line_color="#FFFFFF",
            marker_line_width=1,
        )

    return fig


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">Foresight Demand & Inventory Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Demand forecasting and inventory risk intelligence</div>',
    unsafe_allow_html=True
)


# =========================================================
# API CONNECTION
# =========================================================

API_URL = "http://127.0.0.1:8000"

try:

    response = requests.get(
        f"{API_URL}/risk",
        timeout=10
    )

    if response.status_code == 200:

        risk_data = response.json()
        risk_df = pd.DataFrame(risk_data)

        # =================================================
        # MAIN NAVIGATION
        # =================================================

        st.sidebar.markdown(
            """
            <div style="padding:5px 4px 18px 4px;">
                <div style="font-size:25px;font-weight:800;letter-spacing:-0.5px;color:#ffffff !important;">FORESIGHT</div>
                <div style="font-size:12px;color:#cfc5df !important;margin-top:4px;">Demand &amp; Inventory Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.sidebar.markdown("## 🧭 Navigation")
        st.sidebar.caption("Choose a section to explore")

        page = st.sidebar.radio(
            "Go to",
            [
                "🏠 Home",
                "📊 Overview",
                "📈 Forecast",
                "⚠️ Risk Analysis",
                "🔍 SKU Analysis",
                "🔔 Alerts",
                "📥 Reports"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.sidebar.markdown("---")
        st.sidebar.markdown("**SYSTEM STATUS**")
        st.sidebar.caption("● FastAPI connected")
        st.sidebar.caption("● Risk data loaded")

        # Overall project-level values used by the additional pages.
        home_total_skus = len(risk_df)
        home_critical = (risk_df["Stockout_Risk_Status"] == "Critical").sum()
        home_warning = (risk_df["Stockout_Risk_Status"] == "Warning").sum()
        home_normal = (risk_df["Stockout_Risk_Status"] == "Normal").sum()
        home_overstock = (risk_df["Stockout_Risk_Status"] == "Overstock").sum()
        home_lost_revenue = risk_df["Projected_Lost_Revenue"].sum()
        home_current_stock = risk_df["Current_Stock"].sum()
        home_on_order = risk_df["On_Order"].sum()

        def page_header(title, subtitle):
            st.markdown(
                f'<div class="main-title">{title}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="subtitle">{subtitle}</div>',
                unsafe_allow_html=True
            )

        def simple_card(title, value, css_class="kpi-blue", icon=""):
            return f"""
            <div class="kpi-card {css_class}">
                <div class="kpi-title">{icon} {title}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """

        # ---------------------------------------------------------
        # HOME
        # ---------------------------------------------------------
        if page == "🏠 Home":
            page_header(
                "Welcome to Foresight",
                "Monitor demand forecasts, inventory risk and stockout exposure from one place."
            )

            st.markdown(
                """
                <div style="background:linear-gradient(135deg,#7f45df 0%,#a05aff 46%,#1bcfb4 100%);padding:30px 32px;border-radius:18px;margin-bottom:28px;box-shadow:0 10px 28px rgba(105,70,160,0.16);position:relative;overflow:hidden;">
                    <div style="position:absolute;width:220px;height:220px;border-radius:50%;background:rgba(255,255,255,0.12);right:-70px;top:-100px;"></div>
                    <div style="position:absolute;width:170px;height:170px;border-radius:50%;background:rgba(255,255,255,0.08);right:90px;bottom:-115px;"></div>
                    <div style="position:relative;color:#f4ecff;font-size:12px;font-weight:800;letter-spacing:1.1px;">DEMAND &amp; INVENTORY INTELLIGENCE</div>
                    <div style="position:relative;color:white;font-size:31px;font-weight:800;margin-top:8px;letter-spacing:-0.5px;">Plan smarter. Monitor faster.</div>
                    <div style="position:relative;color:#f4fbff;font-size:15px;margin-top:9px;max-width:760px;">Explore forecasts, inventory risk, SKU-level insights, alerts and downloadable reports from one place.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown('<div class="section-title">At a Glance</div>', unsafe_allow_html=True)
            h1, h2, h3, h4 = st.columns(4)
            with h1:
                st.markdown(simple_card("Total SKUs", f"{home_total_skus:,}", "kpi-blue", "📦"), unsafe_allow_html=True)
            with h2:
                st.markdown(simple_card("Critical SKUs", f"{home_critical:,}", "kpi-critical", "🔴"), unsafe_allow_html=True)
            with h3:
                st.markdown(simple_card("Warning SKUs", f"{home_warning:,}", "kpi-warning", "⚠️"), unsafe_allow_html=True)
            with h4:
                st.markdown(simple_card("Forecast Horizon", "30 days", "kpi-purple", "📈"), unsafe_allow_html=True)

            st.markdown('<div class="section-title">Quick Insights</div>', unsafe_allow_html=True)
            q1, q2 = st.columns(2)
            with q1:
                st.info(f"🔴 **Critical inventory:** {home_critical} SKU(s) require immediate attention.")
                st.warning(f"🟠 **Reorder attention:** {((risk_df['Current_Stock'] < risk_df['Calculated_Reorder_Point']).sum())} SKU(s) are below their reorder point.")
                st.info(f"🔵 **Overstock:** {home_overstock} SKU(s) are currently classified as overstock.")
            with q2:
                st.success("📊 **Forecast:** Explore predicted demand and revenue by SKU.")
                st.metric("Projected Lost Revenue", f"₹{home_lost_revenue:,.0f}")
                st.metric("Inventory Position", f"{home_current_stock + home_on_order:,.0f} units", f"{home_current_stock:,.0f} current + {home_on_order:,.0f} on order")

            st.markdown('<div class="section-title">Quick Navigation</div>', unsafe_allow_html=True)
            n1, n2, n3 = st.columns(3)
            with n1:
                st.markdown("**📊 Overview**\n\nComplete overview with filters, KPIs and charts.")
                st.markdown("**📈 Forecast**\n\nSKU-level demand and revenue forecast.")
            with n2:
                st.markdown("**⚠️ Risk Analysis**\n\nReorder gaps, stockout exposure and risk metrics.")
                st.markdown("**🔍 SKU Analysis**\n\nInventory position and SKU-level details.")
            with n3:
                st.markdown("**🔔 Alerts**\n\nCritical, reorder and overstock alerts.")
                st.markdown("**📥 Reports**\n\nDownload filtered inventory and forecast data.")

            st.caption("Use the navigation menu in the sidebar to open any section.")
            st.stop()

        # ---------------------------------------------------------
        # FORECAST PAGE
        # ---------------------------------------------------------
        if page == "📈 Forecast":
            page_header("Demand Forecast", "Explore predicted demand and revenue for an individual SKU.")
            sku_list_page = sorted(risk_df["SKU"].dropna().unique().tolist())
            f1, f2 = st.columns([2, 1])
            with f1:
                forecast_sku_page = st.selectbox("Select SKU", sku_list_page, key="forecast_page_sku")
            with f2:
                forecast_days_page = st.selectbox("Forecast Horizon", [7, 14, 30, 60, 90], index=2, key="forecast_page_days")

            fr = requests.get(f"{API_URL}/forecast/{forecast_sku_page}?days={forecast_days_page}", timeout=30)
            if fr.status_code == 200:
                fdf = pd.DataFrame(fr.json())
                fdf["Date"] = pd.to_datetime(fdf["Date"])
                total_units = fdf["Forecast_Units"].sum()
                total_revenue = fdf["Forecast_Revenue"].sum()
                avg_units = fdf["Forecast_Units"].mean()
                peak_units = fdf["Forecast_Units"].max()

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Forecast Units", f"{total_units:,.0f}")
                with c2: st.metric("Forecast Revenue", f"₹{total_revenue:,.0f}")
                with c3: st.metric("Average Daily Demand", f"{avg_units:,.2f}")
                with c4: st.metric("Peak Daily Demand", f"{peak_units:,.2f}")

                fig_fp = px.line(fdf, x="Date", y="Forecast_Units", markers=True, title=f"Demand Forecast — {forecast_sku_page}")
                fig_fp.update_layout(height=430, xaxis_title="Date", yaxis_title="Forecast Units", hovermode="x unified")
                st.plotly_chart(
                    style_chart(fig_fp, "line"), use_container_width=True)

                fig_fr = px.area(fdf, x="Date", y="Forecast_Revenue", title=f"Forecast Revenue — {forecast_sku_page}")
                fig_fr.update_layout(height=400, xaxis_title="Date", yaxis_title="Revenue (₹)", hovermode="x unified")
                st.plotly_chart(
                    style_chart(fig_fr, "area"), use_container_width=True)

                with st.expander("View forecast data"):
                    st.dataframe(style_table(fdf, "cyan"), use_container_width=True, hide_index=True, height=table_height(fdf, 420))
            else:
                st.error(f"Forecast API failed: {fr.status_code}")
            st.stop()

        # ---------------------------------------------------------
        # RISK ANALYSIS PAGE
        # ---------------------------------------------------------
        if page == "⚠️ Risk Analysis":
            page_header("Inventory Risk Analysis", "Understand stockout exposure, reorder requirements and inventory position.")
            r1, r2, r3, r4 = st.columns(4)
            with r1: st.metric("Critical", home_critical)
            with r2: st.metric("Warning", home_warning)
            with r3: st.metric("Normal", home_normal)
            with r4: st.metric("Overstock", home_overstock)

            risk_page_df = risk_df.copy()
            risk_page_df["Days_of_Stock_Remaining"] = risk_page_df["Current_Stock"] / risk_page_df["Avg_Daily_Demand"].replace(0, pd.NA)
            risk_page_df["Reorder_Gap"] = (risk_page_df["Calculated_Reorder_Point"] - risk_page_df["Current_Stock"]).clip(lower=0)
            risk_page_df["Additional_Reorder_Qty"] = (risk_page_df["Calculated_Reorder_Point"] - risk_page_df["Current_Stock"] - risk_page_df["On_Order"]).clip(lower=0)

            rr1, rr2, rr3, rr4 = st.columns(4)
            with rr1: st.metric("Below Reorder Point", int((risk_page_df["Reorder_Gap"] > 0).sum()))
            with rr2: st.metric("Projected Stockout Risk", int((risk_page_df["Projected_Stock"] < 0).sum()))
            with rr3: st.metric("Total Reorder Gap", f"{risk_page_df['Reorder_Gap'].sum():,.0f} units")
            with rr4: st.metric("Additional Reorder Qty", f"{risk_page_df['Additional_Reorder_Qty'].sum():,.0f} units")

            st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
            rc = risk_page_df["Stockout_Risk_Status"].value_counts().reset_index()
            rc.columns = ["Risk Status", "SKU Count"]
            fig_rp = px.pie(rc, names="Risk Status", values="SKU Count", hole=0.55, title="SKU Risk Status")
            fig_rp.update_traces(textposition="inside", textinfo="label+percent")
            fig_rp.update_layout(height=420)
            st.plotly_chart(
                style_chart(fig_rp, "pie"), use_container_width=True)

            top_gap = risk_page_df[risk_page_df["Reorder_Gap"] > 0].sort_values("Reorder_Gap", ascending=False).head(10)
            if not top_gap.empty:
                fig_gap = px.bar(top_gap, x="SKU", y="Reorder_Gap", text="Reorder_Gap", title="Top SKUs by Reorder Gap")
                fig_gap.update_traces(texttemplate="%{text:.0f}", textposition="outside")
                fig_gap.update_layout(height=420, yaxis_title="Reorder Gap (Units)")
                st.plotly_chart(
                    style_chart(fig_gap, "default"), use_container_width=True)

            stock_cmp = risk_page_df[["SKU", "Current_Stock", "Calculated_Reorder_Point"]].sort_values("Calculated_Reorder_Point", ascending=False).head(15)
            fig_cmp = px.bar(stock_cmp, x="SKU", y=["Current_Stock", "Calculated_Reorder_Point"], barmode="group", title="Current Stock vs Reorder Point")
            fig_cmp.update_layout(height=440, yaxis_title="Units")
            st.plotly_chart(
                style_chart(fig_cmp, "grouped_bar"), use_container_width=True)

            with st.expander("View risk data"):
                st.dataframe(style_table(risk_page_df, "lavender"), use_container_width=True, hide_index=True, height=table_height(risk_page_df, 520))
            st.stop()

        # ---------------------------------------------------------
        # SKU ANALYSIS PAGE
        # ---------------------------------------------------------
        if page == "🔍 SKU Analysis":
            page_header("SKU Analysis", "Inspect inventory position, demand and risk details for a selected SKU.")
            sku_page_list = sorted(risk_df["SKU"].dropna().unique().tolist())
            selected_sku_page = st.selectbox("Select SKU", sku_page_list, key="sku_analysis_page")
            sku_page_row = risk_df[risk_df["SKU"] == selected_sku_page].iloc[0]

            st.subheader(str(sku_page_row["Product_Name"]))
            st.caption(f"SKU: {sku_page_row['SKU']}")

            s1, s2, s3, s4 = st.columns(4)
            with s1: st.metric("Risk Status", sku_page_row["Stockout_Risk_Status"])
            with s2: st.metric("Current Stock", f"{sku_page_row['Current_Stock']:,.0f}")
            with s3: st.metric("On Order", f"{sku_page_row['On_Order']:,.0f}")
            with s4: st.metric("Lead Time", f"{sku_page_row['Lead_Time_Days']:.0f} days")

            s5, s6, s7, s8 = st.columns(4)
            with s5: st.metric("Avg Daily Demand", f"{sku_page_row['Avg_Daily_Demand']:.2f}")
            with s6: st.metric("Safety Stock", f"{sku_page_row['Calculated_Safety_Stock']:,.0f}")
            with s7: st.metric("Reorder Point", f"{sku_page_row['Calculated_Reorder_Point']:,.0f}")
            with s8: st.metric("Projected Stock", f"{sku_page_row['Projected_Stock']:,.0f}")

            st.markdown('<div class="section-title">Inventory Position</div>', unsafe_allow_html=True)
            sku_chart_df = pd.DataFrame({
                "Metric": ["Current Stock", "On Order", "Safety Stock", "Reorder Point"],
                "Units": [sku_page_row["Current_Stock"], sku_page_row["On_Order"], sku_page_row["Calculated_Safety_Stock"], sku_page_row["Calculated_Reorder_Point"]]
            })
            fig_sp = px.bar(sku_chart_df, x="Metric", y="Units", text="Units", title=f"Inventory Position — {selected_sku_page}")
            fig_sp.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            fig_sp.update_layout(height=430, showlegend=False)
            st.plotly_chart(
                style_chart(fig_sp, "default"), use_container_width=True)

            st.markdown('<div class="section-title">SKU Risk Details</div>', unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            with d1:
                st.metric("Expected Lead-Time Demand", f"{sku_page_row['Expected_Demand_LeadTime']:,.0f}")
                st.metric("Lost Units", f"{sku_page_row['Lost_Units']:,.0f}")
            with d2:
                st.metric("Projected Lost Revenue", f"₹{sku_page_row['Projected_Lost_Revenue']:,.0f}")
                st.metric("Selling Price", f"₹{sku_page_row['Selling_Price']:,.2f}")
            st.stop()

        # ---------------------------------------------------------
        # ALERTS PAGE
        # ---------------------------------------------------------
        if page == "🔔 Alerts":
            page_header("Inventory Alerts", "Review critical, reorder and overstock situations that need attention.")
            critical_page = risk_df[risk_df["Stockout_Risk_Status"] == "Critical"].copy()
            reorder_page = risk_df[risk_df["Current_Stock"] < risk_df["Calculated_Reorder_Point"]].copy()
            overstock_page = risk_df[risk_df["Stockout_Risk_Status"] == "Overstock"].copy()

            a1, a2, a3 = st.columns(3)
            with a1: st.metric("Critical Alerts", len(critical_page))
            with a2: st.metric("Reorder Alerts", len(reorder_page))
            with a3: st.metric("Overstock Alerts", len(overstock_page))

            if not critical_page.empty:
                st.error(f"⚠️ {len(critical_page)} SKU(s) are at critical stockout risk.")
                st.dataframe(style_table(critical_page[["SKU", "Product_Name", "Current_Stock", "Calculated_Reorder_Point", "Projected_Stock", "Projected_Lost_Revenue"]].sort_values("Projected_Lost_Revenue", ascending=False), "pink"), use_container_width=True, hide_index=True, height=table_height(critical_page, 360))
            else:
                st.success("No critical alerts for the current data.")

            if not reorder_page.empty:
                st.warning(f"🟠 {len(reorder_page)} SKU(s) are below their reorder point.")
                st.dataframe(style_table(reorder_page[["SKU", "Product_Name", "Current_Stock", "Calculated_Reorder_Point", "On_Order"]].sort_values("Calculated_Reorder_Point", ascending=False), "teal"), use_container_width=True, hide_index=True, height=table_height(reorder_page, 330))

            if not overstock_page.empty:
                st.info(f"🔵 {len(overstock_page)} SKU(s) are currently classified as overstock.")
                st.dataframe(style_table(overstock_page[["SKU", "Product_Name", "Current_Stock", "On_Order", "Avg_Daily_Demand"]], "cyan"), use_container_width=True, hide_index=True, height=table_height(overstock_page, 330))
            st.stop()

        # ---------------------------------------------------------
        # REPORTS PAGE
        # ---------------------------------------------------------
        if page == "📥 Reports":
            page_header("Reports & Downloads", "Export inventory risk and forecast information for further analysis.")
            st.markdown('<div class="section-title">Inventory Risk Report</div>', unsafe_allow_html=True)
            st.write(f"The current dataset contains **{home_total_skus} SKUs** with **{home_critical} critical**, **{home_warning} warning**, **{home_normal} normal** and **{home_overstock} overstock** records.")
            report_csv = risk_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Inventory Risk CSV", report_csv, "inventory_risk_report.csv", "text/csv", use_container_width=True)

            st.markdown('<div class="section-title">Forecast Report</div>', unsafe_allow_html=True)
            report_skus = sorted(risk_df["SKU"].dropna().unique().tolist())
            report_sku = st.selectbox("Select SKU for forecast report", report_skus, key="report_sku")
            report_days = st.selectbox("Forecast Horizon", [7, 14, 30, 60, 90], index=2, key="report_days")
            report_response = requests.get(f"{API_URL}/forecast/{report_sku}?days={report_days}", timeout=30)
            if report_response.status_code == 200:
                report_forecast_df = pd.DataFrame(report_response.json())
                forecast_report_csv = report_forecast_df.to_csv(index=False).encode("utf-8")
                st.download_button("📈 Download Forecast CSV", forecast_report_csv, f"forecast_{report_sku}.csv", "text/csv", use_container_width=True)
                st.dataframe(style_table(report_forecast_df, "lavender"), use_container_width=True, hide_index=True, height=table_height(report_forecast_df, 420))
            else:
                st.error(f"Forecast API failed: {report_response.status_code}")
            st.stop()

        # =================================================
        # SIDEBAR FILTERS
        # =================================================

        # =================================================

        st.sidebar.markdown("## 🔎 Dashboard Filters")
        st.sidebar.caption("Select a filter to update the dashboard")

        all_risk_df = risk_df.copy()


        # -----------------------------
        # Category Filter
        # -----------------------------

        category_options = ["All Categories"] + sorted(
            all_risk_df["Category"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_category = st.sidebar.selectbox(
            "Category",
            category_options,
            index=0
        )

        if selected_category == "All Categories":

            category_filtered_df = all_risk_df.copy()

        else:

            category_filtered_df = all_risk_df[
                all_risk_df["Category"] == selected_category
            ].copy()


        # -----------------------------
        # Subcategory Filter
        # -----------------------------

        subcategory_options = ["All Subcategories"] + sorted(
            category_filtered_df["Subcategory"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_subcategory = st.sidebar.selectbox(
            "Subcategory",
            subcategory_options,
            index=0
        )

        if selected_subcategory == "All Subcategories":

            subcategory_filtered_df = category_filtered_df.copy()

        else:

            subcategory_filtered_df = category_filtered_df[
                category_filtered_df["Subcategory"] == selected_subcategory
            ].copy()


        # -----------------------------
        # Risk Status Filter
        # -----------------------------

        risk_options = [
            "All Risk Statuses",
            "Critical",
            "Warning",
            "Normal",
            "Overstock"
        ]

        selected_risk = st.sidebar.selectbox(
            "Risk Status",
            risk_options,
            index=0
        )

        if selected_risk == "All Risk Statuses":

            risk_filtered_df = subcategory_filtered_df.copy()

        else:

            risk_filtered_df = subcategory_filtered_df[
                subcategory_filtered_df["Stockout_Risk_Status"] == selected_risk
            ].copy()


        # -----------------------------
        # SKU Filter
        # -----------------------------

        sku_options = ["All SKUs"] + sorted(
            risk_filtered_df["SKU"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_sku_filter = st.sidebar.selectbox(
            "SKU",
            sku_options,
            index=0
        )

        if selected_sku_filter == "All SKUs":

            risk_df = risk_filtered_df.copy()

        else:

            risk_df = risk_filtered_df[
                risk_filtered_df["SKU"] == selected_sku_filter
            ].copy()


        # -----------------------------
        # Filter Summary
        # -----------------------------

        st.sidebar.markdown("---")

        st.sidebar.metric(
            "SKUs in View",
            f"{len(risk_df):,}"
        )


        if risk_df.empty:

            st.warning(
                "No inventory records match the selected filters. "
                "Please change one or more filters."
            )

            st.stop()


        # =================================================
        # KPI CALCULATIONS
        # =================================================

        total_skus = len(risk_df)

        critical_count = (
            risk_df["Stockout_Risk_Status"] == "Critical"
        ).sum()

        warning_count = (
            risk_df["Stockout_Risk_Status"] == "Warning"
        ).sum()

        normal_count = (
            risk_df["Stockout_Risk_Status"] == "Normal"
        ).sum()

        overstock_count = (
            risk_df["Stockout_Risk_Status"] == "Overstock"
        ).sum()

        total_current_stock = risk_df["Current_Stock"].sum()

        total_on_order = risk_df["On_Order"].sum()

        total_lost_revenue = risk_df[
            "Projected_Lost_Revenue"
        ].sum()

        avg_daily_demand = risk_df[
            "Avg_Daily_Demand"
        ].mean()


        # =================================================
        # INVENTORY OVERVIEW
        # =================================================

        st.markdown(
            '<div class="section-title">Inventory Overview</div>',
            unsafe_allow_html=True
        )


        # -------- Row 1 --------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                f"""
                <div class="kpi-card kpi-blue">
                    <div class="kpi-title">Total SKUs</div>
                    <div class="kpi-value">{total_skus:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="kpi-card kpi-critical">
                    <div class="kpi-title">Critical SKUs</div>
                    <div class="kpi-value">{critical_count:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                f"""
                <div class="kpi-card kpi-warning">
                    <div class="kpi-title">Warning SKUs</div>
                    <div class="kpi-value">{warning_count:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:

            st.markdown(
                f"""
                <div class="kpi-card kpi-normal">
                    <div class="kpi-title">Normal SKUs</div>
                    <div class="kpi-value">{normal_count:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # -------- Row 2 --------

        st.write("")

        col5, col6, col7, col8 = st.columns(4)

        with col5:

            st.markdown(
                f"""
                <div class="kpi-card kpi-overstock">
                    <div class="kpi-title">Overstock SKUs</div>
                    <div class="kpi-value">{overstock_count:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col6:

            st.markdown(
                f"""
                <div class="kpi-card kpi-teal">
                    <div class="kpi-title">Current Stock</div>
                    <div class="kpi-value">{total_current_stock:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col7:

            st.markdown(
                f"""
                <div class="kpi-card kpi-purple">
                    <div class="kpi-title">On Order</div>
                    <div class="kpi-value">{total_on_order:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col8:

            st.markdown(
                f"""
                <div class="kpi-card kpi-revenue">
                    <div class="kpi-title">Projected Lost Revenue</div>
                    <div class="kpi-value">₹{total_lost_revenue:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # RISK DISTRIBUTION
        # =================================================

        st.markdown(
            '<div class="section-title">Inventory Risk Distribution</div>',
            unsafe_allow_html=True
        )

        risk_counts = (
            risk_df["Stockout_Risk_Status"]
            .value_counts()
            .reset_index()
        )

        risk_counts.columns = [
            "Risk Status",
            "SKU Count"
        ]

        fig = px.pie(
            risk_counts,
            names="Risk Status",
            values="SKU Count",
            hole=0.55,
            title="SKU Risk Status"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="label+percent"
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            ),
            legend_title="Risk Status"
        )

        st.plotly_chart(

            style_chart(fig, "pie"),
            use_container_width=True
        )


        # =================================================
        # EXTRA KPI
        # =================================================

        col9, col10 = st.columns(2)

        with col9:

            st.metric(
                "Average Daily Demand",
                f"{avg_daily_demand:.2f} units"
            )

        with col10:

            critical_revenue = risk_df.loc[
                risk_df["Stockout_Risk_Status"] == "Critical",
                "Projected_Lost_Revenue"
            ].sum()

            st.metric(
                "Critical SKU Lost Revenue",
                f"₹{critical_revenue:,.0f}"
            )


        # =================================================
        # DEMAND FORECAST
        # =================================================

        st.markdown(
            '<div class="section-title">Demand Forecast</div>',
            unsafe_allow_html=True
        )


        # -------- Forecast Controls --------

        forecast_col1, forecast_col2 = st.columns([2, 1])

        with forecast_col1:

            sku_list = sorted(
                risk_df["SKU"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_sku = st.selectbox(
                "Select SKU",
                sku_list
            )

        with forecast_col2:

            forecast_days = st.selectbox(
                "Forecast Horizon",
                [7, 14, 30, 60, 90],
                index=2
            )


        # -------- Get Forecast From API --------

        forecast_response = requests.get(
            f"{API_URL}/forecast/{selected_sku}?days={forecast_days}",
            timeout=30
        )

        if forecast_response.status_code == 200:

            forecast_df = pd.DataFrame(
                forecast_response.json()
            )

            forecast_df["Date"] = pd.to_datetime(
                forecast_df["Date"]
            )


            # -----------------------------
            # Forecast KPIs
            # -----------------------------

            total_forecast_units = forecast_df[
                "Forecast_Units"
            ].sum()

            total_forecast_revenue = forecast_df[
                "Forecast_Revenue"
            ].sum()

            average_daily_forecast = forecast_df[
                "Forecast_Units"
            ].mean()


            fc1, fc2, fc3 = st.columns(3)

            with fc1:

                st.metric(
                    "Forecast Units",
                    f"{total_forecast_units:,.0f}"
                )

            with fc2:

                st.metric(
                    "Forecast Revenue",
                    f"₹{total_forecast_revenue:,.0f}"
                )

            with fc3:

                st.metric(
                    "Average Daily Demand",
                    f"{average_daily_forecast:,.2f}"
                )


            # -----------------------------
            # Forecast Chart
            # -----------------------------

            fig_forecast = px.line(
                forecast_df,
                x="Date",
                y="Forecast_Units",
                markers=True,
                title=f"Demand Forecast — {selected_sku}"
            )

            fig_forecast.update_layout(
                height=450,
                xaxis_title="Date",
                yaxis_title="Forecast Units",
                hovermode="x unified"
            )

            st.plotly_chart(

                style_chart(fig_forecast, "line"),
                use_container_width=True
            )


            # -----------------------------
            # Forecast Revenue Chart
            # -----------------------------

            fig_revenue = px.area(
                forecast_df,
                x="Date",
                y="Forecast_Revenue",
                title=f"Forecast Revenue — {selected_sku}"
            )

            fig_revenue.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Revenue (₹)",
                hovermode="x unified"
            )

            st.plotly_chart(

                style_chart(fig_revenue, "area"),
                use_container_width=True
            )

        else:

            st.error(
                f"Forecast API failed: {forecast_response.status_code}"
            )


        # =================================================
        # SKU ANALYSIS
        # =================================================

        st.markdown(
            '<div class="section-title">SKU Analysis</div>',
            unsafe_allow_html=True
        )


        # Get selected SKU information
        selected_sku_data = risk_df[
            risk_df["SKU"] == selected_sku
        ].copy()


        if not selected_sku_data.empty:

            sku_info = selected_sku_data.iloc[0]


            # -----------------------------
            # SKU Profile
            # -----------------------------

            # Use native Streamlit text here instead of custom HTML.
            # This prevents the HTML source from ever appearing as code.
            st.subheader(str(sku_info["Product_Name"]))
            st.caption(f"SKU: {sku_info['SKU']}")


            # -----------------------------
            # Basic Information
            # -----------------------------

            info_col1, info_col2, info_col3 = st.columns(3)

            with info_col1:

                st.markdown(
                    f"""
                    <div class="info-label">Category</div>
                    <div class="info-value">{sku_info["Category"]}</div>

                    <div class="info-label">Subcategory</div>
                    <div class="info-value">{sku_info["Subcategory"]}</div>

                    <div class="info-label">Risk Status</div>
                    <div class="info-value">{sku_info["Stockout_Risk_Status"]}</div>
                    """,
                    unsafe_allow_html=True
                )

            with info_col2:

                st.markdown(
                    f"""
                    <div class="info-label">Current Stock</div>
                    <div class="info-value">{sku_info["Current_Stock"]:,.0f} units</div>

                    <div class="info-label">On Order</div>
                    <div class="info-value">{sku_info["On_Order"]:,.0f} units</div>

                    <div class="info-label">Lead Time</div>
                    <div class="info-value">{sku_info["Lead_Time_Days"]:.0f} days</div>
                    """,
                    unsafe_allow_html=True
                )

            with info_col3:

                st.markdown(
                    f"""
                    <div class="info-label">Average Daily Demand</div>
                    <div class="info-value">{sku_info["Avg_Daily_Demand"]:.2f} units</div>

                    <div class="info-label">Safety Stock</div>
                    <div class="info-value">{sku_info["Calculated_Safety_Stock"]:,.0f} units</div>

                    <div class="info-label">Reorder Point</div>
                    <div class="info-value">{sku_info["Calculated_Reorder_Point"]:,.0f} units</div>
                    """,
                    unsafe_allow_html=True
                )


            st.write("")


            # -----------------------------
            # SKU Inventory KPIs
            # -----------------------------

            sku_kpi1, sku_kpi2, sku_kpi3, sku_kpi4 = st.columns(4)

            with sku_kpi1:

                st.metric(
                    "Projected Stock",
                    f'{sku_info["Projected_Stock"]:,.0f}'
                )

            with sku_kpi2:

                st.metric(
                    "Expected Lead-Time Demand",
                    f'{sku_info["Expected_Demand_LeadTime"]:,.0f}'
                )

            with sku_kpi3:

                st.metric(
                    "Lost Units",
                    f'{sku_info["Lost_Units"]:,.0f}'
                )

            with sku_kpi4:

                st.metric(
                    "Projected Lost Revenue",
                    f'₹{sku_info["Projected_Lost_Revenue"]:,.0f}'
                )


            # -----------------------------
            # Stock vs Reorder Point Chart
            # -----------------------------

            stock_chart_df = pd.DataFrame({
                "Metric": [
                    "Current Stock",
                    "On Order",
                    "Safety Stock",
                    "Reorder Point"
                ],
                "Units": [
                    sku_info["Current_Stock"],
                    sku_info["On_Order"],
                    sku_info["Calculated_Safety_Stock"],
                    sku_info["Calculated_Reorder_Point"]
                ]
            })


            fig_stock = px.bar(
                stock_chart_df,
                x="Metric",
                y="Units",
                text="Units",
                title=f"Inventory Position — {selected_sku}"
            )

            fig_stock.update_traces(
                texttemplate="%{text:.0f}",
                textposition="outside"
            )

            fig_stock.update_layout(
                height=430,
                xaxis_title="Inventory Metric",
                yaxis_title="Units",
                showlegend=False
            )

            st.plotly_chart(

                style_chart(fig_stock, "default"),
                use_container_width=True
            )


        # =================================================
        # STOCKOUT & REORDER ANALYSIS
        # =================================================

        st.markdown(
            '<div class="section-title">Stockout & Reorder Analysis</div>',
            unsafe_allow_html=True
        )


        # -----------------------------
        # Reorder Calculations
        # -----------------------------

        reorder_df = risk_df.copy()

        reorder_df["Days_of_Stock_Remaining"] = (
            reorder_df["Current_Stock"] /
            reorder_df["Avg_Daily_Demand"].replace(0, pd.NA)
        )

        reorder_df["Reorder_Gap"] = (
            reorder_df["Calculated_Reorder_Point"] -
            reorder_df["Current_Stock"]
        ).clip(lower=0)

        reorder_df["Additional_Reorder_Qty"] = (
            reorder_df["Calculated_Reorder_Point"] -
            reorder_df["Current_Stock"] -
            reorder_df["On_Order"]
        ).clip(lower=0)


        # -----------------------------
        # Reorder KPIs
        # -----------------------------

        reorder_needed_count = (
            reorder_df["Reorder_Gap"] > 0
        ).sum()

        stockout_risk_count = (
            reorder_df["Projected_Stock"] < 0
        ).sum()

        total_reorder_gap = reorder_df[
            "Reorder_Gap"
        ].sum()

        total_additional_reorder = reorder_df[
            "Additional_Reorder_Qty"
        ].sum()


        reorder_col1, reorder_col2, reorder_col3, reorder_col4 = st.columns(4)

        with reorder_col1:

            st.metric(
                "SKUs Below Reorder Point",
                f"{reorder_needed_count:,}"
            )

        with reorder_col2:

            st.metric(
                "Projected Stockout Risk",
                f"{stockout_risk_count:,}"
            )

        with reorder_col3:

            st.metric(
                "Total Reorder Gap",
                f"{total_reorder_gap:,.0f} units"
            )

        with reorder_col4:

            st.metric(
                "Additional Reorder Qty",
                f"{total_additional_reorder:,.0f} units"
            )


        # -----------------------------
        # Reorder Attention Table
        # -----------------------------

        st.markdown(
            "### 🔄 Reorder Attention"
        )

        reorder_attention_df = reorder_df[
            reorder_df["Reorder_Gap"] > 0
        ][
            [
                "SKU",
                "Product_Name",
                "Stockout_Risk_Status",
                "Current_Stock",
                "On_Order",
                "Calculated_Reorder_Point",
                "Reorder_Gap",
                "Additional_Reorder_Qty",
                "Days_of_Stock_Remaining"
            ]
        ].sort_values(
            "Reorder_Gap",
            ascending=False
        )


        if reorder_attention_df.empty:

            st.success(
                "No SKUs are currently below their reorder point."
            )

        else:

            st.dataframe(
                style_table(reorder_attention_df, "teal"),
                use_container_width=True,
                hide_index=True,
                height=table_height(reorder_attention_df, 480)
            )


        # -----------------------------
        # Top Reorder Gap Chart
        # -----------------------------

        top_reorder_df = reorder_attention_df.head(10).copy()

        if not top_reorder_df.empty:

            fig_reorder = px.bar(
                top_reorder_df,
                x="SKU",
                y="Reorder_Gap",
                text="Reorder_Gap",
                title="Top SKUs by Reorder Gap"
            )

            fig_reorder.update_traces(
                texttemplate="%{text:.0f}",
                textposition="outside"
            )

            fig_reorder.update_layout(
                height=430,
                xaxis_title="SKU",
                yaxis_title="Reorder Gap (Units)",
                showlegend=False
            )

            st.plotly_chart(

                style_chart(fig_reorder, "default"),
                use_container_width=True
            )


        # -----------------------------
        # Lowest Days of Stock Remaining
        # -----------------------------

        st.markdown(
            "### 📉 Lowest Days of Stock Remaining"
        )

        days_stock_df = reorder_df[
            [
                "SKU",
                "Product_Name",
                "Stockout_Risk_Status",
                "Current_Stock",
                "Avg_Daily_Demand",
                "Days_of_Stock_Remaining"
            ]
        ].sort_values(
            "Days_of_Stock_Remaining",
            ascending=True
        ).head(10)


        fig_days = px.bar(
            days_stock_df,
            x="SKU",
            y="Days_of_Stock_Remaining",
            text="Days_of_Stock_Remaining",
            title="SKUs with Lowest Remaining Stock Days"
        )

        fig_days.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig_days.update_layout(
            height=430,
            xaxis_title="SKU",
            yaxis_title="Days of Stock Remaining",
            showlegend=False
        )

        st.plotly_chart(

            style_chart(fig_days, "default"),
            use_container_width=True
        )


        # =================================================
        # INVENTORY RISK ANALYSIS
        # =================================================

        st.markdown(
            '<div class="section-title">Inventory Risk Analysis</div>',
            unsafe_allow_html=True
        )


        # -----------------------------
        # Risk KPIs
        # -----------------------------

        risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)

        with risk_col1:

            st.metric(
                "Critical",
                f"{critical_count:,}"
            )

        with risk_col2:

            st.metric(
                "Warning",
                f"{warning_count:,}"
            )

        with risk_col3:

            st.metric(
                "Normal",
                f"{normal_count:,}"
            )

        with risk_col4:

            st.metric(
                "Overstock",
                f"{overstock_count:,}"
            )


        # -----------------------------
        # Current Stock vs Reorder Point
        # -----------------------------

        stock_comparison_df = risk_df[
            [
                "SKU",
                "Current_Stock",
                "Calculated_Reorder_Point"
            ]
        ].copy()

        stock_comparison_df = stock_comparison_df.sort_values(
            "Calculated_Reorder_Point",
            ascending=False
        ).head(15)


        fig_stock_comparison = px.bar(
            stock_comparison_df,
            x="SKU",
            y=[
                "Current_Stock",
                "Calculated_Reorder_Point"
            ],
            barmode="group",
            title="Current Stock vs Reorder Point"
        )

        fig_stock_comparison.update_layout(
            height=450,
            xaxis_title="SKU",
            yaxis_title="Units"
        )

        st.plotly_chart(

            style_chart(fig_stock_comparison, "grouped_bar"),
            use_container_width=True
        )


        # -----------------------------
        # Top Risky SKUs
        # -----------------------------

        top_risk_df = risk_df[
            [
                "SKU",
                "Projected_Lost_Revenue"
            ]
        ].sort_values(
            "Projected_Lost_Revenue",
            ascending=False
        ).head(10)


        fig_risk = px.bar(
            top_risk_df,
            x="SKU",
            y="Projected_Lost_Revenue",
            title="Top SKUs by Projected Lost Revenue",
            text="Projected_Lost_Revenue"
        )

        fig_risk.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside"
        )

        fig_risk.update_layout(
            height=450,
            xaxis_title="SKU",
            yaxis_title="Projected Lost Revenue (₹)"
        )

        st.plotly_chart(

            style_chart(fig_risk, "coral_bar"),
            use_container_width=True
        )


        # -----------------------------
        # Critical Inventory Alerts
        # -----------------------------

        st.markdown(
            "### 🚨 Critical Inventory Alerts"
        )

        critical_df = risk_df[
            risk_df["Stockout_Risk_Status"] == "Critical"
        ][
            [
                "SKU",
                "Product_Name",
                "Current_Stock",
                "Calculated_Reorder_Point",
                "Projected_Stock",
                "Projected_Lost_Revenue"
            ]
        ].sort_values(
            "Projected_Lost_Revenue",
            ascending=False
        )


        if critical_df.empty:

            st.success(
                "No critical inventory alerts for the current filters."
            )

        else:

            st.dataframe(
                style_table(critical_df, "pink"),
                use_container_width=True,
                hide_index=True,
                height=table_height(critical_df, 360)
            )


        # =================================================
        # INVENTORY ALERTS
        # =================================================

        st.markdown(
            '<div class="section-title">🚨 Inventory Alerts</div>',
            unsafe_allow_html=True
        )

        critical_alerts = risk_df[
            risk_df["Stockout_Risk_Status"] == "Critical"
        ].copy()

        reorder_alerts = risk_df[
            risk_df["Current_Stock"] < risk_df["Calculated_Reorder_Point"]
        ].copy()

        overstock_alerts = risk_df[
            risk_df["Stockout_Risk_Status"] == "Overstock"
        ].copy()

        alert_col1, alert_col2, alert_col3 = st.columns(3)

        with alert_col1:
            st.metric(
                "Critical Alerts",
                len(critical_alerts)
            )

        with alert_col2:
            st.metric(
                "Reorder Alerts",
                len(reorder_alerts)
            )

        with alert_col3:
            st.metric(
                "Overstock Alerts",
                len(overstock_alerts)
            )

        if not critical_alerts.empty:

            st.error(
                f"⚠️ {len(critical_alerts)} SKU(s) are at critical stockout risk."
            )

            st.dataframe(
                style_table(
                    critical_alerts[
                        [
                            "SKU",
                            "Product_Name",
                            "Current_Stock",
                            "Calculated_Reorder_Point",
                            "Projected_Stock",
                            "Projected_Lost_Revenue"
                        ]
                    ].sort_values(
                        "Projected_Lost_Revenue",
                        ascending=False
                    ),
                    "pink"
                ),
                use_container_width=True,
                hide_index=True,
                height=table_height(critical_alerts, 360)
            )

        elif not reorder_alerts.empty:

            st.warning(
                f"⚠️ {len(reorder_alerts)} SKU(s) are below their reorder point."
            )

        else:

            st.success(
                "No critical or reorder alerts for the current filters."
            )

        # =================================================
        # EXPORT / DOWNLOAD
        # =================================================

        st.markdown(
            '<div class="section-title">Export & Download</div>',
            unsafe_allow_html=True
        )

        export_col1, export_col2 = st.columns(2)

        with export_col1:

            risk_csv = risk_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Download Inventory Risk CSV",
                data=risk_csv,
                file_name="inventory_risk_filtered.csv",
                mime="text/csv",
                use_container_width=True
            )

        with export_col2:

            if "forecast_df" in locals() and not forecast_df.empty:

                forecast_csv = forecast_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="📥 Download Forecast CSV",
                    data=forecast_csv,
                    file_name=f"forecast_{selected_sku}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            else:

                st.info(
                    "Forecast data is not available for download right now."
                )


        # =================================================
        # API & SYSTEM STATUS
        # =================================================

        st.markdown(
            '<div class="section-title">API & System Status</div>',
            unsafe_allow_html=True
        )

        # Check FastAPI health endpoint
        try:
            health_response = requests.get(
                f"{API_URL}/health",
                timeout=5
            )
            api_online = health_response.status_code == 200
        except requests.exceptions.RequestException:
            health_response = None
            api_online = False

        status_col1, status_col2, status_col3, status_col4 = st.columns(4)

        with status_col1:
            st.metric(
                "FastAPI Service",
                "🟢 Online" if api_online else "🔴 Offline"
            )

        with status_col2:
            st.metric(
                "Risk Data",
                "🟢 Available" if response.status_code == 200 else "🔴 Error"
            )

        with status_col3:
            forecast_api_ok = (
                "forecast_response" in locals()
                and forecast_response.status_code == 200
            )
            st.metric(
                "Forecast Service",
                "🟢 Available" if forecast_api_ok else "🔴 Error"
            )

        with status_col4:
            if api_online and health_response is not None:
                st.metric(
                    "API Response",
                    f"{health_response.status_code} OK"
                )
            else:
                st.metric(
                    "API Response",
                    "Unavailable"
                )

        if api_online:
            st.success(
                "All connected services are responding. The dashboard is ready to use."
            )
        else:
            st.warning(
                "FastAPI is not responding. Please make sure Uvicorn is running on port 8000."
            )


        # =================================================
        # INVENTORY RISK DATA TABLE
        # =================================================

        st.markdown(
            '<div class="section-title">Inventory Risk Data</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            style_table(risk_df, "lavender"),
            use_container_width=True,
            hide_index=True,
            height=table_height(risk_df, 560)
        )


    else:

        st.error(
            f"API connection failed. Status code: {response.status_code}"
        )


except requests.exceptions.RequestException:

    st.error(
        "Could not connect to the FastAPI server. "
        "Please make sure Uvicorn is running on port 8000."
    )