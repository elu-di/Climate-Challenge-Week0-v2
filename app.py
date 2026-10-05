import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_countries, COUNTRY_COLORS, COUNTRY_FILES

# ── Page configuration ─────────────────────────────────────────────────────────
# This MUST be the first Streamlit call in the script.
st.set_page_config(
    page_title="African Climate Dashboard",
    page_icon="🌍",
    layout="wide",
)




# ── Load data ──────────────────────────────────────────────────────────────────
df_all = load_all_countries("data/raw")

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("🌍 Climate Filters")
st.sidebar.markdown("---")

# Country selector (multi-select, all selected by default)
all_countries = list(COUNTRY_FILES.keys())
selected_countries = st.sidebar.multiselect(
    label="Select Countries",
    options=all_countries,
    default=all_countries,
)

# Year range slider
min_year = int(df_all["YEAR"].min())
max_year = int(df_all["YEAR"].max())
year_range = st.sidebar.slider(
    label="Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

# Climate variable selector
variable_options = {
    "Mean Temperature (°C)":   "T2M",
    "Precipitation (mm/day)":  "PRECTOTCORR",
    "Relative Humidity (%)":   "RH2M",
    "Wind Speed (m/s)":        "WS2M",
}
selected_label = st.sidebar.selectbox(
    label="Climate Variable",
    options=list(variable_options.keys()),
)
selected_var = variable_options[selected_label]

st.sidebar.markdown("---")
st.sidebar.caption("Data source: NASA POWER · 2015–2026")

# ── Filter the DataFrame based on sidebar selections ───────────────────────────
df_filtered = df_all[
    (df_all["Country"].isin(selected_countries)) &
    (df_all["YEAR"] >= year_range[0]) &
    (df_all["YEAR"] <= year_range[1])
].copy()


# ── Main Page ──────────────────────────────────────────────────────────────────
st.title("🌍 African Climate Dashboard")
st.markdown("Comparing temperature and precipitation trends across **5 African countries** (2015–2026).")
st.markdown("---")

# Guard: if user deselects all countries, show a warning and stop
if not selected_countries:
    st.warning("⚠️ Please select at least one country from the sidebar.")
    st.stop()

# ── KPI Metric Cards ───────────────────────────────────────────────────────────
st.subheader("📊 Summary Statistics")

cols = st.columns(len(selected_countries))

for i, country in enumerate(selected_countries):
    country_data = df_filtered[df_filtered["Country"] == country]
    avg_temp     = country_data["T2M"].mean()
    total_rain   = country_data.groupby("YEAR")["PRECTOTCORR"].sum().mean()
    avg_humidity = country_data["RH2M"].mean()

    with cols[i]:
        st.markdown(f"**{country}**")
        st.metric("Avg Temp (°C)",     f"{avg_temp:.1f} °C")
        st.metric("Avg Annual Rain",   f"{total_rain:.0f} mm")
        st.metric("Avg Humidity (%)",  f"{avg_humidity:.1f} %")

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Trends", "🌦 Seasonality", "🔥 Correlations"])

# ── Tab 1: Trends Over Time ────────────────────────────────────────────────────
with tab1:
    st.subheader(f"{selected_label} — Monthly Trend ({year_range[0]}–{year_range[1]})")

    # Aggregate by Country and Year-Month
    df_trends = df_filtered.copy()
    df_trends["YearMonth"] = df_trends["Date"].dt.to_period("M").dt.to_timestamp()

    if selected_var == "PRECTOTCORR":
        monthly_data = (
            df_trends.groupby(["Country", "YearMonth"])["PRECTOTCORR"]
            .sum()
            .reset_index()
        )
        y_axis_title = "Total Monthly Rainfall (mm)"
    else:
        monthly_data = (
            df_trends.groupby(["Country", "YearMonth"])[selected_var]
            .mean()
            .reset_index()
        )
        y_axis_title = f"Mean {selected_label}"

    fig_trend, ax_trend = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        data=monthly_data,
        x="YearMonth",
        y=selected_var,
        hue="Country",
        palette=COUNTRY_COLORS,
        linewidth=2,
        ax=ax_trend,
    )
    ax_trend.set_title(
        f"{selected_label} Monthly Progression", fontsize=13, fontweight="bold"
    )
    ax_trend.set_xlabel("Date", fontsize=11)
    ax_trend.set_ylabel(y_axis_title, fontsize=11)
    ax_trend.grid(True, linestyle="--", alpha=0.4)
    ax_trend.legend(title="Country", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    st.pyplot(fig_trend)
    plt.close(fig_trend)

    # If rainfall is selected, also display annual total rainfall comparison
    if selected_var == "PRECTOTCORR":
        st.markdown("#### 🌧 Annual Total Rainfall Trend")
        annual_precip = (
            df_filtered.groupby(["Country", "YEAR"])["PRECTOTCORR"].sum().reset_index()
        )
        fig_annual, ax_annual = plt.subplots(figsize=(10, 4))
        sns.lineplot(
            data=annual_precip,
            x="YEAR",
            y="PRECTOTCORR",
            hue="Country",
            palette=COUNTRY_COLORS,
            marker="s",
            linewidth=2,
            ax=ax_annual,
        )
        ax_annual.set_title(
            f"Annual Total Rainfall ({year_range[0]}–{year_range[1]})",
            fontsize=12,
            fontweight="bold",
        )
        ax_annual.set_xlabel("Year", fontsize=11)
        ax_annual.set_ylabel("Total Annual Rainfall (mm)", fontsize=11)
        ax_annual.grid(True, linestyle="--", alpha=0.4)
        ax_annual.legend(
            title="Country", bbox_to_anchor=(1.02, 1), loc="upper left"
        )
        plt.tight_layout()
        st.pyplot(fig_annual)
        plt.close(fig_annual)


# ── Tab 2: Seasonality & Distributions ─────────────────────────────────────────
with tab2:
    st.subheader(f"{selected_label} — Seasonal Cycle (Jan–Dec)")

    # 1. 12-Month Calendar Cycle
    if selected_var == "PRECTOTCORR":
        monthly_totals = (
            df_filtered.groupby(["Country", "YEAR", "Month"])["PRECTOTCORR"]
            .sum()
            .reset_index()
        )
        seasonal_cycle = (
            monthly_totals.groupby(["Country", "Month"])["PRECTOTCORR"]
            .mean()
            .reset_index()
        )
        y_season_label = "Average Monthly Rainfall (mm)"
    else:
        seasonal_cycle = (
            df_filtered.groupby(["Country", "Month"])[selected_var]
            .mean()
            .reset_index()
        )
        y_season_label = f"Average {selected_label}"

    fig_season, ax_season = plt.subplots(figsize=(11, 4.5))
    sns.lineplot(
        data=seasonal_cycle,
        x="Month",
        y=selected_var,
        hue="Country",
        palette=COUNTRY_COLORS,
        marker="o",
        linewidth=2.5,
        ax=ax_season,
    )
    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    ax_season.set_xticks(range(1, 13))
    ax_season.set_xticklabels(month_labels)
    ax_season.set_title(
        f"Mean Seasonal Cycle for {selected_label}",
        fontsize=13,
        fontweight="bold",
    )
    ax_season.set_xlabel("Calendar Month", fontsize=11)
    ax_season.set_ylabel(y_season_label, fontsize=11)
    ax_season.grid(True, linestyle="--", alpha=0.4)
    ax_season.legend(
        title="Country", bbox_to_anchor=(1.02, 1), loc="upper left"
    )
    plt.tight_layout()
    st.pyplot(fig_season)
    plt.close(fig_season)

    # 2. Boxplot Distribution
    st.markdown("#### 📦 Distribution by Country")
    fig_box, ax_box = plt.subplots(figsize=(10, 4))
    sns.boxplot(
        data=df_filtered,
        x="Country",
        y=selected_var,
        palette=COUNTRY_COLORS,
        order=selected_countries,
        ax=ax_box,
    )
    ax_box.set_title(
        f"Daily {selected_label} Distribution", fontsize=12, fontweight="bold"
    )
    ax_box.set_xlabel("Country", fontsize=11)
    ax_box.set_ylabel(selected_label, fontsize=11)
    ax_box.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_box)
    plt.close(fig_box)


# ── Tab 3: Correlations & ML Insights ──────────────────────────────────────────
with tab3:
    st.subheader("🔥 Climate Variable Correlation Matrices")
    features = ["T2M", "PRECTOTCORR", "RH2M", "WS2M", "PS"]
    feature_labels = {
        "T2M": "Temp",
        "PRECTOTCORR": "Rain",
        "RH2M": "Humidity",
        "WS2M": "Wind",
        "PS": "Pressure",
    }

    # Render heatmaps for each selected country side by side
    n_cols = len(selected_countries)
    fig_corr, axes = plt.subplots(1, n_cols, figsize=(max(5 * n_cols, 8), 4))
    if n_cols == 1:
        axes = [axes]

    for i, country in enumerate(selected_countries):
        subset = (
            df_filtered[df_filtered["Country"] == country][features]
            .rename(columns=feature_labels)
        )
        corr_matrix = subset.corr()

        sns.heatmap(
            corr_matrix,
            ax=axes[i],
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            cbar=(i == n_cols - 1),
        )
        axes[i].set_title(f"{country}", fontweight="bold", fontsize=12)

    plt.tight_layout()
    st.pyplot(fig_corr)
    plt.close(fig_corr)

    # Summary table of correlations with Precipitation
    st.markdown("#### 🎯 Linear Correlation with Daily Precipitation (`PRECTOTCORR`)")
    precip_corr = {}
    for country in selected_countries:
        subset = df_filtered[df_filtered["Country"] == country]
        precip_corr[country] = (
            subset[features].corr()["PRECTOTCORR"].drop("PRECTOTCORR").round(3)
        )

    df_precip_corr = pd.DataFrame(precip_corr).rename(index=feature_labels)
    st.dataframe(df_precip_corr.T, use_container_width=True)

    with st.expander("💡 Key Climate & Modeling Insights"):
        st.markdown(
            """
            - **Strongest Rain Predictor:** Across all countries, **Relative Humidity (`RH2M`)** shows the highest positive correlation (+0.35 to +0.51) with daily precipitation.
            - **Non-Linear Dynamics:** Daily mean temperature (`T2M`) shows near-zero linear correlation with precipitation. Tree-based models or non-linear regressors are required to capture climate threshold dynamics.
            - **Seasonal Contrast:** Ethiopia experiences a unimodal July–August peak (*Kiremt*), while Kenya shows a bimodal cycle (April *Long Rains* and November *Short Rains*). Models must condition on country/coordinates rather than raw calendar month alone.
            """
        )

