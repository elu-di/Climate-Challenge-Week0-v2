# 🌍 African Climate Insights Dashboard (2015–2026)

[![CI](https://github.com/elu-di/Climate-Challenge-Week0-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/elu-di/Climate-Challenge-Week0-v2/actions/workflows/ci.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end climate analysis pipeline and interactive Streamlit web dashboard analyzing **11 years of daily NASA POWER satellite observations (2015–2026)** across **5 East and West African nations**: **Ethiopia**, **Kenya**, **Nigeria**, **Sudan**, and **Tanzania**.

---

## 📌 Executive Summary & Key Findings

Understanding regional climate dynamics and precipitation predictability is critical for climate resilience, agricultural planning, and food security across Sub-Saharan Africa. This project investigates $20,540$ daily observations to uncover macro-level trends, seasonal signatures, and machine learning implications:

1. **Seasonal Regimes Differ Fundamentally by Geography:**
   - **Ethiopia (Unimodal Summer):** Driven by the *Kiremt* rains peaking sharply in July and August (~$300\text{ mm/month}$).
   - **Kenya (Equatorial Bimodal):** Features two distinct rainy seasons—the *Long Rains* (April) and *Short Rains* (November)—separated by dry intervals.
   - **Tanzania (Southern East Africa):** Long wet season from November through May, followed by a dry winter (June–September).
   - **Sudan (Hyper-Arid):** A brief, narrow rainfall window strictly in July–August.

2. **Drought Vulnerability & Margins:**
   - **High Rainfall Group:** Nigeria (~$1,443\text{ mm/yr}$), Tanzania (~$1,280\text{ mm/yr}$), and Ethiopia (~$1,244\text{ mm/yr}$).
   - **Arid & Semi-Arid Group:** Kenya (~$503\text{ mm/yr}$) and Sudan (~$220\text{ mm/yr}$). Operating on thin rainfall margins, slight seasonal anomalies create disproportionate drought risks in these regions.

3. **Machine Learning & Feature Engineering Takeaways:**
   - **Top Linear Rain Predictor:** Across all countries, **Relative Humidity (`RH2M`)** shows the highest positive linear correlation with precipitation ($r \approx +0.35$ to $+0.51$).
   - **Non-Linear Dynamics:** Daily mean temperature (`T2M`) has near-zero linear correlation with precipitation. Forecasting extreme rainfall or drought cannot rely on simple linear models—tree ensembles (e.g. Random Forest, XGBoost) or neural networks are essential to capture atmospheric moisture threshold effects.
   - **Spatial Conditioning:** Calendar months cannot be used as raw global inputs without geographic context (e.g. July is peak rainy season in Ethiopia, but dry season in Tanzania).

---

## 🖥 Dashboard Features

The interactive dashboard ([`app.py`](app.py)) provides researchers and decision-makers with real-time exploratory tools:

- **Interactive Sidebar:**
  - Multi-select country filter (any combination of 1 to 5 nations)
  - Interactive year range slider ($2015$–$2026$)
  - Climate variable selector (`T2M`, `PRECTOTCORR`, `RH2M`, `WS2M`)
- **Responsive KPI Metric Cards:** Dynamic summary statistics (average temperature, mean annual rainfall, and average humidity) that automatically re-render based on selected countries.
- **Tab 1: 📈 Trends:** Multi-year monthly progression line charts with custom country color palettes, plus annual rainfall accumulation comparisons.
- **Tab 2: 🌦 Seasonality:** Aggregated 12-month calendar cycles (Jan–Dec) paired with distribution boxplots to analyze variance and extreme events.
- **Tab 3: 🔥 Correlations:** Side-by-side Pearson correlation heatmaps, linear rainfall correlation summary tables, and ML takeaways.

---

## 📂 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow (pytest on Python 3.11)
├── data/
│   └── raw/                   # NASA POWER daily CSV datasets for all 5 countries
├── notebooks/
│   └── compare_countries.ipynb# Exploratory Data Analysis & statistical comparisons
├── src/
│   ├── __init__.py
│   └── data_loader.py         # Modular loader, data cleaning pipeline & @st.cache_data
├── tests/
│   ├── __init__.py
│   └── test_data_loader.py    # Automated unit tests for data integrity and transformations
├── app.py                     # Main interactive Streamlit dashboard application
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository

```bash
git clone https://github.com/elu-di/Climate-Challenge-Week0-v2.git
cd Climate-Challenge-Week0-v2
```

### 2. Set Up a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Streamlit Dashboard

```bash
streamlit run app.py
```

The app will launch in your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

Automated testing is configured using `pytest` to ensure data cleaning integrity and schema consistency:

```bash
pytest -v
```

All 6 test cases validate:
- Expected country mappings and color themes
- Complete row count ($20,540$ rows; $4,108$ per country)
- Required meteorological columns
- Datetime formatting and month extraction ($1$–$12$)
- Conversion of sentinel missing values (`-999` to `NaN`)
- Path validation and error handling

---

## 📊 Data Source

Data retrieved from the **NASA POWER (Prediction Of Worldwide Energy Resources)** Project:
- **Spatial Resolution:** Point-location coordinates representing agricultural & capital centers
- **Temporal Coverage:** Daily observations from January 1, 2015 to December 31, 2026
- **Key Variables:**
  - `T2M`: Temperature at 2 Meters (°C)
  - `PRECTOTCORR`: Total Precipitation Corrected (mm/day)
  - `RH2M`: Relative Humidity at 2 Meters (%)
  - `WS2M`: Wind Speed at 2 Meters (m/s)
  - `PS`: Surface Pressure (kPa)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
