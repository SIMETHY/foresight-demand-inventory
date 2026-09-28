# 📈 Foresight Demand & Inventory Analytics Dashboard

An end-to-end **Power BI Analytics Solution** built to optimize supply chain decisions, track inventory stockout risks, evaluate predictive machine learning models, and plan 30-day forward demand.
---
## 📌 Executive Summary
This project bridges data science and supply chain management by combining historical sales data, machine learning demand forecasting models, and interactive dashboard UI. It gives inventory planning teams immediate visibility into stock health, risk exposure, and future demand requirements.

### Key Portfolio Metrics & Results:
- **Total Historical Revenue:** ₹3.10 Billion[cite: 5]
- **Total Units Sold:** 511.8K Units[cite: 5]
- **30-Day Forecasted Sales Revenue:** ₹125.3 Million[cite: 8]
- **30-Day Projected Demand:** ~21K Units[cite: 8]
- **Best Model Forecast Accuracy ($R^2$):** 76.90% (HistGradientBoosting)[cite: 7]
- **Forecast Error Rate (WAPE):** 22.24%[cite: 7]

---

## 🛠️ Tech Stack & Skills
- **Business Intelligence & Reporting:** Power BI, DAX, Custom KPI Cards, Interactive Slicers[cite: 2, 5, 6, 7, 8]
- **Machine Learning & Modeling:** HistGradientBoosting, Random Forest, Ridge Regression, Moving Average[cite: 7]
- **Model Evaluation Metrics:** $R^2$ Accuracy Score, WAPE %, MAE (2.76), RMSE (3.56)[cite: 7]
- **Supply Chain Analytics:** Stockout Risk Categorization, Safety Stock / Reorder Point Tracking, Holding Cost Risk, Days of Supply[cite: 5, 6]

---

## 📊 Dashboard Overview & Visual Breakdown

### 1. Executive Overview - Demand & Inventory Report
Provides executive leadership with high-level KPI cards and top-tier category performance[cite: 5].
- **Key Indicators:** Tracks Total Revenue (₹3.10bn), Units Sold (511.8K), Forecasted Sales Revenue (₹125.3M), and Projected Lost Revenue (₹3.17M)[cite: 5].
- **Actual vs. 30-Day Forecasted Demand:** Time-series line chart comparing historical unit sales against future forecast trends[cite: 5].
- **Category Revenue Breakdown:** Ranks sales performance led by **Home Decor (₹0.89bn)**, **Furniture (₹0.60bn)**, and **Storage (₹0.58bn)**[cite: 5].
- **Inventory Risk Distribution:** Donut chart categorizing stock risk into Overstock (62%), Warning (18%), Critical (10%), and Normal (10%)[cite: 5].

---

### 2. Inventory Optimization & Risk Action Desk
Focuses on operational actionability to prevent stockouts and reduce excess holding costs[cite: 6].
- **Risk Exposure Analysis:** Highlights 5 Critical Risk SKUs and 31 Overstock SKUs[cite: 6].
- **Stockout Danger Zone Scatter:** Maps current stock levels against reorder points to flag items requiring immediate stock replenishment[cite: 6].
- **Risk Exposure by Category:** Compares total projected lost revenue against estimated holding cost risk (led by Storage holding risk at ₹3.1M)[cite: 6].
- **Average Days of Supply:** Tracks category buffer stock (Storage: 35 days vs. Home Decor: 14 days; Overall Average: 22.2 days)[cite: 6].
- **Action Matrix:** Detailed table listing individual SKU reorder thresholds, stock counts, and projected revenue loss (e.g., SKU012 critical status)[cite: 6].

---

### 3. Demand Forecast Accuracy & Model Intelligence
Evaluates machine learning model reliability for predictive analytics transparency[cite: 7].
- **Model Benchmarking:** Compares HistGradientBoosting (Best), Random Forest, Ridge Regression, and a 7-Day Moving Average baseline[cite: 7].
- **Precision Metrics:** Tracks Model $R^2$ (76.90%), WAPE Error (22.24%), Mean Absolute Error (2.76), and Root Mean Squared Error (3.56)[cite: 7].
- **Actual vs. Predicted Demand (Test Set):** Evaluates test dataset performance across peak and trough cycles[cite: 7].
- **Residual Variance by Category:** Analyzes over/under-forecasting bias across Home Decor, Kitchen, Lighting, Furniture, and Storage[cite: 7].

---

### 4. 30-Day Predictive Sales & Inventory Planning
Supports short-term supply chain operations and purchasing schedules[cite: 8].
- **Forward Forecast Trend:** Daily projection tracking unit demand spikes over a 30-day window[cite: 8].
- **30-Day Projected Demand by Category:** Identifies volume drivers led by Home Decor (~5.4K units)[cite: 8].
- **Promotional Lift Analysis:** Measures demand variations across product lines[cite: 8].
- **SKU Demand Matrix:** Granular lookup for individual product forecasts and expected revenue (analyzing 50 SKUs in total)[cite: 8].

---

## 📁 Project Structure
├── data/                                          # Raw & processed supply chain datasets
├── models/                                        # ML forecasting & risk models
├── notebooks/                                     # Data prep & exploratory data analysis
├── Foresight Demand Inventory Final Output..pbix  # Main Interactive Power BI Dashboard File
└── Power_BI_README.md                             # Documentation

---

## 🚀 How to View & Explore
1. Download the [`Foresight Demand Inventory Final Output..pbix`](./Foresight%20Demand%20Inventory%20Final%20Output..pbix) file[cite: 2, 4].
2. Open the file in **Power BI Desktop**[cite: 2].
3. Use the top slicers (**Category**, **Model**, **SKU**, **Risk Level**) to filter metrics interactively across all four report pages[cite: 5, 6, 7, 8].

---
