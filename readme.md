# FORESIGHT: Autonomous Demand Forecasting & Inventory Risk Intelligence

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-FF4B4B.svg)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7+-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Enterprise-grade machine learning platform for end-to-end retail supply chain planning, recursive multi-step demand forecasting, dynamic safety stock optimization, and stockout revenue loss mitigation.**

---

## 📌 Executive Summary

Retail supply chains face twin financial perils: **stockouts** leading to permanent lost revenue and customer churn, versus **overstocking** which ties up crucial working capital in depreciating inventory.

**FORESIGHT** solves this by unifying historical sales, replenishment lead times, promotional calendars, and inventory snapshots into an intelligent closed-loop forecasting and risk engine:
1. **Recursive ML Forecasting**: Predicts SKU-level unit demand 30 days ahead using HistGradientBoosting regressors enriched with temporal cyclical encodings and rolling lag features.
2. **Dynamic Risk & Safety Stock Engine**: Calculates statistical Safety Stock ($Z = 1.65$ for 95% service level) and forward-looking Reorder Points (ROP) factoring supplier lead times.
3. **Financial Quantification**: Quantifies lost revenue risks and working capital locks for every SKU, generating automated replenishment purchase recommendations.
4. **Multi-Interface Deployment**: Serves real-time inference via an enterprise **FastAPI** service and an executive **Streamlit Dashboard**.

---

## 🏗️ System Architecture

```
                                 ┌─────────────────────────┐
                                 │       Raw Sources       │
                                 │ Sales, Inventory, SKU,  │
                                 │     Calendar Events     │
                                 └────────────┬────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │  Milestone 1: ETL & Star Schema │
                             │  • Schema Validation & Cleaning │
                             │  • Orphan SKU Isolation         │
                             │  • Star-Schema Warehouse Export │
                             └────────────────┬────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │ Milestone 3: ML Forecast Engine │
                             │  • 27 Lag & Rolling Features    │
                             │  • Cyclical Calendar Encodings  │
                             │  • Temporal Train/Test Split    │
                             │  • 30-Day Recursive Multi-Step  │
                             └────────────────┬────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │  Milestone 4: Risk Scoring      │
                             │  • Dynamic Safety Stock (Z=1.65)│
                             │  • Lead-Time Stock Projections  │
                             │  • 4-Tier Risk Categorization   │
                             │  • Lost Revenue & Capital Locks │
                             └────────────────┬────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
        ┌─────────────────────────┐                       ┌─────────────────────────┐
        │  FastAPI REST Service   │                       │   Streamlit Dashboard   │
        │  • /health, /skus       │                       │  • Executive Risk KPIs  │
        │  • /forecast/{sku}      │                       │  • 30-Day Forecast Viz  │
        │  • /risk/{sku}          │                       │  • SKU Stock Analytics  │
        └─────────────────────────┘                       └─────────────────────────┘
```

---

## 📊 Model Evaluation & Benchmarks

All models were evaluated across 50 SKUs using a strict **temporal train/test split** (no lookahead leakage). **HistGradientBoosting** demonstrated superior non-linear pattern capture across seasonal spikes and promotion lifts:

| Model | MAE (Units) | RMSE | WAPE (%) | $R^2$ Score | Status |
|---|:---:|:---:|:---:|:---:|:---:|
| **7-Day Moving Avg (Baseline)** | 3.221 | 4.224 | 25.95% | 0.675 | Baseline |
| **Ridge Regression (L2)** | 2.881 | 3.700 | 23.21% | 0.751 | Benchmark |
| **Random Forest Regressor** | 2.799 | 3.614 | 22.55% | 0.762 | Benchmark |
| **HistGradientBoosting (FORESIGHT)** | **2.761** | **3.559** | **22.24%** | **0.769** | **Champion** |

*WAPE reduction of **3.71 percentage points** over moving average baseline, achieving 76.9% variance explanation on unseen test demand.*

---

## 🧮 Inventory Optimization & Risk Logic

### 1. Dynamic Safety Stock ($SS$)
Calculated at a **95% Service Level** ($Z = 1.65$) to buffer against demand volatility during replenishment lead times:
$$SS = Z \times \sigma_{\text{demand}} \times \sqrt{L}$$
*(where $\sigma_{\text{demand}}$ is SKU daily demand standard deviation, and $L$ is supplier lead time in days)*

### 2. Forward-Looking Reorder Point ($ROP$)
$$ROP = (\bar{d}_{\text{forecast}} \times L) + SS$$
*(where $\bar{d}_{\text{forecast}}$ is the ML projected mean daily demand over the next 30 days)*

### 3. Lead-Time Projected Stock & Classification
$$\text{Projected Stock} = \text{Current Stock} + \text{On Order} - (\bar{d}_{\text{forecast}} \times L)$$

- 🚨 **Critical**: $\text{Projected Stock} < 0$ (imminent stockout gap requiring expedited purchase order).
- ⚠️ **Warning**: $0 \le \text{Projected Stock} < SS$ (stock projected into safety buffer).
- 🟢 **Normal**: $SS \le \text{Projected Stock} \le 2.5 \times SS$ (balanced inventory health).
- 📦 **Overstock**: $\text{Projected Stock} > 2.5 \times SS$ (excess capital tied up).

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/SIMETHY/foresight-demand-inventory.git
cd foresight-demand-inventory
```

### 2. Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 4. Run the FastAPI REST Service
```bash
uvicorn api.main:app --reload --port 8000
```
Interactive Swagger docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|:---:|---|
| `/health` | `GET` | Health check and service readiness |
| `/skus` | `GET` | Retrieve list of all 50 active SKU IDs |
| `/forecast/{sku}?days=30` | `GET` | On-demand recursive forward forecast for target SKU |
| `/forecast` | `GET` | Batch 30-day forward demand projections for all SKUs |
| `/risk/{sku}` | `GET` | Safety stock, ROP, stockout gap, and lost revenue risk for single SKU |
| `/risk?status=Critical` | `GET` | Filtered portfolio risk table by status (`Critical`, `Warning`, `Overstock`) |

---

## 📁 Repository Directory Structure

```
foresight-demand-inventory/
├── api/
│   └── main.py                                    # FastAPI REST scoring service (M6)
├── dashboard/
│   └── app.py                                     # Advanced custom-styled Streamlit UI
├── data/
│   ├── raw/                                       # Source datasets (sales, inventory, sku, calendar)
│   └── processed/                                 # Fact/dim tables, forecasts, risk scores
├── models/
│   └── demand_forecaster.joblib                   # Production HistGradientBoosting model artifact
├── notebooks/
│   ├── 01_data_pipeline.ipynb                     # ETL validation & star-schema creation
│   ├── 02_EDA.ipynb                               # Exploratory analysis & seasonality decomposition
│   ├── 03_demand_forecasting.ipynb                # Feature engineering & model benchmarking
│   └── 04_risk_scoring.ipynb                      # Safety stock & financial risk calculations
├── src/
│   ├── data_pipeline.py                           # Production ETL pipeline script
│   ├── forecasting.py                             # ML training & 30-day recursive forecast engine
│   └── risk_scoring.py                            # Inventory risk & replenishment engine
├── app.py                                         # Streamlit root application
├── Foresight Demand Inventory Final Output..pbix  # Interactive Power BI Report
├── PROJECT_REPORT.md                              # Comprehensive Technical Project Report
├── Power_BI_readme.md                             # Power BI documentation & visual breakdown
├── requirements.txt                               # Pinned production dependencies
└── README.md                                      # Platform documentation
```

---

## 👥 Contributors & Acknowledgements
- Developed for **FORESIGHT Demand & Inventory Intelligence Platform**.
- Built with Python, Scikit-Learn, FastAPI, Streamlit, and Power BI.
