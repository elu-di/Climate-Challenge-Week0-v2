import pytest
import pandas as pd
from pathlib import Path

from src.data_loader import (
    load_all_countries,
    _clean_country,
    COUNTRY_FILES,
    COUNTRY_COLORS,
)


@pytest.fixture(scope="module")
def df_all():
    """Load the full dataset once for the test suite."""
    return load_all_countries("data/raw")


def test_country_files_and_colors_keys():
    """Verify that both mappings define the expected 5 African countries."""
    expected = {"Ethiopia", "Kenya", "Nigeria", "Sudan", "Tanzania"}
    assert set(COUNTRY_FILES.keys()) == expected
    assert set(COUNTRY_COLORS.keys()) == expected


def test_load_all_countries_shape_and_presence(df_all):
    """Ensure all 5 countries are loaded with expected total row count."""
    assert isinstance(df_all, pd.DataFrame)
    assert len(df_all) == 20540
    assert set(df_all["Country"].unique()) == set(COUNTRY_FILES.keys())

    # Each country should have exactly 4,108 daily observations (2015-2026)
    for country in COUNTRY_FILES.keys():
        assert (df_all["Country"] == country).sum() == 4108


def test_required_columns_exist(df_all):
    """Verify all primary climate features and metadata columns exist."""
    required = [
        "YEAR",
        "DOY",
        "Date",
        "Month",
        "Country",
        "T2M",
        "PRECTOTCORR",
        "RH2M",
        "WS2M",
        "PS",
    ]
    for col in required:
        assert col in df_all.columns, f"Missing required column: {col}"


def test_date_and_month_parsing(df_all):
    """Ensure Date is parsed to datetime and Month is within 1-12."""
    assert pd.api.types.is_datetime64_any_dtype(df_all["Date"])
    assert df_all["Month"].min() == 1
    assert df_all["Month"].max() == 12
    assert df_all["Date"].dt.year.min() == 2015
    assert df_all["Date"].dt.year.max() == 2026


def test_sentinel_missing_values_removed(df_all):
    """Verify that NASA POWER sentinel missing value (-999) has been converted to NaN."""
    numeric_cols = df_all.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_cols:
        assert not (df_all[col] == -999).any(), f"Sentinel -999 found in column {col}"
        assert not (df_all[col] == -999.0).any(), f"Sentinel -999.0 found in column {col}"


def test_invalid_data_dir_raises_error():
    """Verify that FileNotFoundError is raised when an invalid path is passed."""
    with pytest.raises(FileNotFoundError):
        load_all_countries("data/nonexistent_folder_xyz")
