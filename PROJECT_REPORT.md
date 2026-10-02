# PROJECT FORESIGHT
## Autonomous Demand Forecasting & Inventory Risk Intelligence
### Comprehensive Project Technical Report

**Project Track:** AI & Machine Learning in Supply Chain / Enterprise Operations  
**Date of Submission:** October 2, 2026  
**Repository:** [GitHub: foresight-demand-inventory](https://github.com/SIMETHY/foresight-demand-inventory)  
**System Deployment:** Streamlit Cloud & FastAPI REST Microservice  

---

## 1. Executive Summary

In contemporary retail and omnichannel supply chains, inaccurate inventory planning inflicts a dual financial penalty: **stockouts** generate immediate lost sales, damage customer retention, and lose market share to competitors; concurrently, **overstocking** traps working capital in non-liquid inventory, increases warehousing holding costs, and heightens shrinkage risk.

**Project FORESIGHT** is an enterprise-grade artificial intelligence and decision-support platform designed to replace legacy, static moving-average inventory heuristics with closed-loop predictive intelligence. The solution unifies historical sales velocity, supplier replenishment lead times, promotional calendar dynamics, and periodic inventory snapshots. 

By operationalizing a **HistGradientBoosting Regressor** with 27 temporal and contextual features, FORESIGHT achieves a **22.24% Weighted Absolute Percentage Error (WAPE)** and an **$R^2$ of 0.769** across 50 active retail SKUs, reducing forecasting error by 3.71 percentage points over standard baselines. These forecasts directly power a dynamic **Safety Stock and Reorder Point (ROP)** optimization engine ($Z = 1.65$ for 95% service level) that quantifies financial exposure in real-time, projects stock balances through replenishment lead times, and outputs prioritized purchase order recommendations via an interactive **Streamlit Dashboard** and **FastAPI REST API**.

---

## 2. Problem Statement & Objectives

### 2.1 The Supply Chain Dilemma
Retail inventory managers operate under extreme uncertainty characterized by:
- Non-stationary demand seasonality (day-of-week surges, promotional lift, public holiday shifts).
- Variable supplier replenishment lead times (ranging from 3 to 21 days across product categories).
- High demand variance leading to either chronic stockouts in fast-moving items or excess holding costs in slow-moving SKUs.

### 2.2 Core Project Objectives
1. **Automated ETL & Data Cleansing:** Build a resilient data pipeline to ingest, clean, validate business keys, and structure retail data into a dimensional star schema.
2. **Predictive Demand Modeling:** Engineer rolling statistics, multi-lag signals, and cyclical temporal encodings to benchmark multiple algorithms and select a champion model for 30-day forward recursive forecasting.
3. **Dynamic Inventory Risk Quantification:** Move beyond static buffer stocks to dynamic safety stocks and lead-time projected stockouts, computing projected revenue losses and working capital locks.
4. **Interactive Enterprise Decision Support:** Deliver an intuitive visual command center (Streamlit) and programmatic API endpoints (FastAPI) enabling immediate procurement decision-making.

---

## 3. Technology Stack

| Layer | Technologies Used | Purpose |
|---|---|---|
| **Core Language** | Python 3.10+ | Primary development, data pipelines, and modeling |
| **Data Processing & ETL** | Pandas, NumPy | Relational operations, schema cleansing, array transformations |
| **Machine Learning** | Scikit-Learn, Joblib | Model benchmarking (Ridge, RF, HistGradientBoosting), persistence |
| **Exploratory Analysis** | Matplotlib, Seaborn | Distribution profiling, demand volatility, lag autocorrelation |
| **Backend Web API** | FastAPI, Uvicorn, Pydantic | High-performance asynchronous REST microservice |
| **Frontend Dashboard** | Streamlit | Interactive decision-support UI with filtering & CSV export |
| **Version Control & CI** | Git, GitHub | Codebase management, release tracking, reproducible pipelines |

---

## 4. End-to-End System Architecture

```
+-----------------------------------------------------------------------------------+
|                                   DATA SOURCES                                    |
|   daily_sales.csv  |  inventory_snapshots.csv  |  sku_master.csv  |  calendar.csv |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        MILESTONE 1: INGESTION & DATA WAREHOUSE                    |
|   * Data type enforcement & date parsing                                          |
|   * Duplicate business key validation (Date + SKU)                                |
|   * Orphan inventory detection (unmatched SKU master records isolated)            |
|   * Dimensional Star Schema: fact_sales_daily, fact_inventory, dim_sku            |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        MILESTONE 3: ML DEMAND FORECASTING                         |
|   * 27 engineered features: Lags (7, 14, 21, 28), Rolling Windows (7, 14, 28)     |
|   * Cyclical temporal signals (sine/cosine of day of week, month)                 |
|   * Temporal train/test split (no lookahead bias)                                 |
|   * Champion Model: HistGradientBoostingRegressor (WAPE: 22.24%, R2: 0.769)       |
|   * Recursive 30-day multi-step forward demand projection                         |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        MILESTONE 4: INVENTORY RISK ENGINE                         |
|   * Demand Volatility: Standard deviation of historical sales                     |
|   * Safety Stock Calculation: SS = 1.65 * sigma * sqrt(Lead_Time)                 |
|   * Reorder Point: ROP = (Forecast_Daily_Demand * Lead_Time) + SS                 |
|   * Lead-Time Projected Stock = Current_Stock + On_Order - LeadTime_Demand        |
|   * 4-Tier Risk Categorization: Critical, Warning, Normal, Overstock              |
|   * Financial Risk: Projected Lost Revenue vs Capital Tied Up                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                   +----------------------+----------------------+
                   v                                             v
+-------------------------------------+       +-------------------------------------+
|        FASTAPI REST SERVICE         |       |         STREAMLIT DASHBOARD         |
|   * GET /health                     |       |   * Executive KPI Scorecards        |
|   * GET /skus                       |       |   * Risk Portfolio Distribution     |
|   * GET /forecast/{sku} (recursive) |       |   * Interactive SKU Forecaster      |
|   * GET /risk?status=Critical       |       |   * Replenishment Action Orders     |
+-------------------------------------+       +-------------------------------------+
```

---

## 5. Methodology & Implementation Details

### 5.1 Data Pipeline & Warehouse Design (Milestone 1)
The raw data inputs consisted of four operational logs:
- `sales_daily.csv`: Transactional sales quantities, pricing, and promotional tags.
- `inventory_snapshots.csv`: Periodic on-hand stock balances, quantities on order, and replenishment lead times.
- `sku_master.csv`: Catalog metadata, product taxonomy (Category, Subcategory), and cost structures.
- `calendar.csv`: Date attributes, calendar holidays, and marketing event schedules.

**Data Hygiene Steps:**
1. Checked for duplicate composite keys `(Date, SKU)` and verified zero duplicate records in `fact_sales_daily`.
2. Validated foreign-key relationships. Isolated orphaned inventory entries (records whose SKU was missing from the catalog) into `data/processed/excluded_inventory_skus.csv` to preserve audit integrity.
3. Transformed clean datasets into a normalized dimensional model stored under `data/processed/`.

### 5.2 Exploratory Data Analysis & Key Insights (Milestone 2)
1. **Demand Seasonality:** Pronounced weekend shopping surges with a secondary midweek lift. Promotions increased sales volume by an average of 42% across high-frequency categories.
2. **Demand Volatility:** Daily sales exhibited non-Gaussian distributions with variance clustering, indicating that traditional standard deviations underestimate tail risks during promotional spikes.
3. **Lead Time Asymmetry:** Replenishment lead times ranged from 3 days for local consumables to 21 days for imported electronic accessories, requiring lead-time-weighted risk thresholds.

### 5.3 Feature Engineering & Model Benchmarking (Milestone 3)
A strict temporal train-test split was enforced where the final 60 days of historical records were withheld for testing.

**Feature Matrix (27 Features):**
- **Autoregressive Lags:** `lag_7`, `lag_14`, `lag_21`, `lag_28` to capture weekly cyclicality.
- **Rolling Windows:** `rolling_mean_7`, `rolling_std_7`, `rolling_mean_14`, `rolling_std_14`, `rolling_mean_28`, `rolling_std_28`, `rolling_min_7`, `rolling_max_7`.
- **Calendar & Cyclical Signals:** Day of week, day of month, month, weekend binary flag, holiday flag, promotion event binary flag, and trigonometric encodings:
  $$\sin\left(\frac{2\pi \cdot \text{day}}{7}\right), \quad \cos\left(\frac{2\pi \cdot \text{day}}{7}\right), \quad \sin\left(\frac{2\pi \cdot \text{month}}{12}\right), \quad \cos\left(\frac{2\pi \cdot \text{month}}{12}\right)$$
- **SKU Metadata:** `Selling_Price`, `Cost_Price`, categorical ordinal IDs for `SKU`, `Category`, and `Subcategory`.

**Benchmark Performance:**
Each candidate model was evaluated using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Weighted Absolute Percentage Error (WAPE), and the coefficient of determination ($R^2$):

$$\text{WAPE} = \frac{\sum_{t=1}^N |y_t - \hat{y}_t|}{\sum_{t=1}^N y_t} \times 100\%$$

| Algorithm | MAE | RMSE | WAPE (%) | $R^2$ | Notes |
|---|:---:|:---:|:---:|:---:|---|
| **7-Day Moving Average Baseline** | 3.221 | 4.224 | 25.95% | 0.675 | Standard industry naive heuristic |
| **Ridge Regression (L2)** | 2.881 | 3.700 | 23.21% | 0.751 | Linear model with regularization |
| **Random Forest Regressor** | 2.799 | 3.614 | 22.55% | 0.762 | Ensemble of 100 decision trees |
| **HistGradientBoostingRegressor** | **2.761** | **3.559** | **22.24%** | **0.769** | **Selected Champion Model** |

**Recursive 30-Day Forecasting:**
Because actual future sales are unknown during multi-step forecasting, FORESIGHT implements an iterative recursive loop: the model generates $t+1$ predictions, dynamically appends them back to the synthetic timeline, recalculates rolling averages and lag features, and steps forward through day $t+30$.

---

## 6. Inventory Risk & Safety Stock Engine (Milestone 4)

Rather than treating forecasting as an isolated exercise, FORESIGHT embeds predictions directly into inventory risk equations.

### 6.1 Formulaic Derivations
1. **Dynamic Safety Stock ($SS$):**
   $$SS = Z \times \sigma_{\text{demand}} \times \sqrt{L}$$
   Where $Z = 1.65$ corresponds to a 95% cycle-service level, $\sigma_{\text{demand}}$ is the historical standard deviation of daily demand for the SKU, and $L$ is the supplier lead time in days.

2. **Forecast-Driven Reorder Point ($ROP$):**
   $$ROP = (\bar{d}_{\text{forecast}} \times L) + SS$$
   Where $\bar{d}_{\text{forecast}}$ is the mean daily forecast generated by the ML model over the 30-day horizon.

3. **Lead-Time Projected Stock ($S_{\text{projected}}$):**
   $$S_{\text{projected}} = \text{Current Stock} + \text{On Order} - (\bar{d}_{\text{forecast}} \times L)$$

### 6.2 Risk Classification Rules
- 🚨 **Critical (Stockout Hazard):** $S_{\text{projected}} < 0$. The pipeline calculates:
  $$\text{Lost Units} = |S_{\text{projected}}|$$
  $$\text{Projected Lost Revenue} = \text{Lost Units} \times \text{Selling Price}$$
- ⚠️ **Warning (Buffer Incursion):** $0 \le S_{\text{projected}} < SS$. On-hand inventory will breach the safety threshold before new shipments arrive.
- 🟢 **Normal (Optimal State):** $SS \le S_{\text{projected}} \le 2.5 \times SS$.
- 📦 **Overstock (Capital Inefficiency):** $S_{\text{projected}} > 2.5 \times SS$.
  $$\text{Excess Units} = S_{\text{projected}} - (2.5 \times SS)$$
  $$\text{Capital Tied Up} = \text{Excess Units} \times \text{Cost Price}$$

---

## 7. User Interfaces & Deployment (Milestones 5 & 6)

### 7.1 Streamlit Interactive Dashboard (`app.py`)
The web application provides supply chain planners with three analytical perspectives:
1. **Executive Overview:** Top-level metrics displaying total monitored SKUs, counts of Critical/Warning/Overstock items, and total portfolio projected lost revenue. Includes interactive charts of risk distribution and stock versus reorder points.
2. **Demand Forecast:** SKU selector displaying 30-day continuous line charts, cumulative projected unit demand, and anticipated sales revenue.
3. **SKU Intelligence & Action Table:** Detailed SKU health cards showing safety stock requirements, supplier lead times, and an instant CSV export feature for procurement teams.

### 7.2 FastAPI REST Microservice (`api/main.py`)
Enables headless, real-time integration into ERP or warehouse management systems:
- `GET /health`: Microservice heartbeat and dependency status.
- `GET /skus`: Enumeration of all catalog items.
- `GET /forecast/{sku}?days=30`: On-demand dynamic recursive forecasting.
- `GET /risk?status=Critical`: Filtered inventory exposure queries for immediate automated PO generation.

---

## 8. Key Challenges Faced & Solutions

| Challenge Encountered | Root Cause | Engineering Solution |
|---|---|---|
| **Lookahead Data Leakage** | Random K-fold cross-validation mixes future information into past predictions. | Implemented strict chronological train/test split preserving time-series arrow of time. |
| **Recursive Error Compounding** | Multi-step recursive forecasting can amplify step errors over 30 days. | Utilized rolling statistical aggregations (min, max, std) which dampen extreme variance propagation. |
| **Catalog Orphan Records** | Inventory snapshots contained SKUs not present in catalog dimensions. | Built automated validation layer that isolates orphan records into audit files without halting pipelines. |
| **Cold Start / Sparse Categories** | Certain low-velocity SKUs have intermittent zero-demand days. | Categorical target encoding and category-level fallback statistics in the ETL engine. |

---

## 9. Conclusion & Business Impact

Project FORESIGHT demonstrates how modern gradient-boosted machine learning combined with classical inventory theory bridges the gap between data science and operational supply chain execution.

**Measurable Outcomes:**
- **3.71% WAPE improvement** over standard moving-average benchmarks across 50 product lines.
- **Quantifiable risk mitigation:** Immediate visibility into critical stockout gaps, allowing procurement officers to reorder prior to stock depletion.
- **Zero-lag operationalization:** Real-time access via both low-latency REST endpoints and an intuitive executive dashboard.

---
*Report compiled autonomously by the FORESIGHT Project Development Team.*
