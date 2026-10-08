import pandas as pd
import streamlit as st
from pathlib import Path


# Country label → raw CSV filename mapping
COUNTRY_FILES = {
    "Ethiopia": "ethiopia (1).csv",
    "Kenya":    "kenya (1).csv",
    "Nigeria":  "nigeria (1).csv",
    "Sudan":    "sudan.csv",
    "Tanzania": "tanzania.csv",
}
# Fixed color palette (consistent across all charts in the dashboard)
COUNTRY_COLORS = {
    "Ethiopia": "#e74c3c",
    "Kenya":    "#3498db",
    "Sudan":    "#f39c12",
    "Tanzania": "#2ecc71",
    "Nigeria":  "#9b59b6",
}
def _clean_country(filepath: Path, country_name: str) -> pd.DataFrame:
    """Load one country's raw CSV, clean it, and tag it with the country name."""
    df = pd.read_csv(filepath)
    df["Country"] = country_name
    # Replace NASA sentinel missing value (-999) with NaN
    df = df.replace([-999, -999.0], float("nan"))
    # Remove exact duplicate rows
    df = df.drop_duplicates()
    # Build a proper Date column from YEAR + DOY (Day Of Year)
    df["Date"] = pd.to_datetime(
        df["YEAR"].astype(str) + df["DOY"].astype(str).str.zfill(3),
        format="%Y%j",
    )
    # Extract calendar month for seasonal analysis
    df["Month"] = df["Date"].dt.month
    return df
@st.cache_data
def load_all_countries(data_dir: str = "data/raw") -> pd.DataFrame:
    """
    Load, clean, and concatenate all 5 country CSV files into one DataFrame.
    The @st.cache_data decorator ensures this runs only ONCE when the app
    starts, and returns the cached DataFrame for every subsequent interaction.
    Args:
        data_dir: path to the folder containing the raw CSV files.
    Returns:
        A single DataFrame with all 5 countries (20,540 rows).
    """
    raw_dir = Path(data_dir)
    if not raw_dir.exists():
        # Fallback: resolve relative to project root (parent of src/)
        raw_dir = Path(__file__).resolve().parent.parent / data_dir

    frames = []
    for country, filename in COUNTRY_FILES.items():
        filepath = raw_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(
                f"Dataset for {country} not found at {filepath.resolve()}."
            )
        frames.append(_clean_country(filepath, country))
    df_all = pd.concat(frames, ignore_index=True)
    return df_all