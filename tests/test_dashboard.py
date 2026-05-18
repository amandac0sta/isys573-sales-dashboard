"""
Tests for ISYS 573 Sales Dashboard
===================================
Run: pytest tests/ -v
"""

import json
import re
import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from dashboard import load_data, build_region_bar, build_monthly_line, \
                      build_category_pie, build_top_products, build_html

DATA_PATH = Path(__file__).parent.parent / "data" / "sales.csv"


@pytest.fixture
def df() -> pd.DataFrame:
    return load_data(DATA_PATH)


class TestLoadData:
    def test_loads_without_error(self, df):
        assert len(df) == 500

    def test_required_columns_present(self, df):
        required = {"date", "region", "category", "product",
                    "units_sold", "unit_price", "revenue", "channel"}
        assert required.issubset(set(df.columns))

    def test_date_parsed_as_datetime(self, df):
        assert pd.api.types.is_datetime64_any_dtype(df["date"])

    def test_quarter_column_added(self, df):
        assert "quarter" in df.columns
        assert set(df["quarter"].unique()).issubset({"Q1", "Q2", "Q3", "Q4"})

    def test_month_column_added(self, df):
        assert "month" in df.columns

    def test_revenue_is_positive(self, df):
        assert (df["revenue"] > 0).all()

    def test_four_regions(self, df):
        assert df["region"].nunique() == 4

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_data(Path("/nonexistent/path.csv"))


class TestRegionChart:
    def test_returns_figure(self, df):
        fig = build_region_bar(df)
        assert fig is not None

    def test_has_four_bars(self, df):
        fig = build_region_bar(df)
        # build_region_bar uses go.Bar (single trace) with one y-value per region
        assert len(fig.data) == 1
        assert len(fig.data[0].y) == 4

    def test_filtered_by_quarter(self, df):
        q1 = df[df["quarter"] == "Q1"]
        fig = build_region_bar(q1)
        # Should only show regions present in Q1
        assert len(fig.data[0].x) <= 4


class TestMonthlyChart:
    def test_returns_figure(self, df):
        fig = build_monthly_line(df)
        assert fig is not None

    def test_has_twelve_months_or_fewer(self, df):
        fig = build_monthly_line(df)
        assert len(fig.data[0].x) <= 12

    def test_revenue_values_are_positive(self, df):
        fig = build_monthly_line(df)
        assert all(v > 0 for v in fig.data[0].y)


class TestCategoryChart:
    def test_returns_figure(self, df):
        fig = build_category_pie(df)
        assert fig is not None

    def test_six_categories(self, df):
        fig = build_category_pie(df)
        assert len(fig.data[0].labels) == 6


class TestTopProducts:
    def test_returns_figure(self, df):
        fig = build_top_products(df)
        assert fig is not None

    def test_default_top_10(self, df):
        fig = build_top_products(df)
        assert len(fig.data[0].y) == 10

    def test_custom_n(self, df):
        fig = build_top_products(df, n=5)
        assert len(fig.data[0].y) == 5

    def test_sorted_ascending_for_horizontal_bar(self, df):
        fig = build_top_products(df)
        revenues = list(fig.data[0].x)
        assert revenues == sorted(revenues)


class TestRegionFilter:
    """Tests for the region filter dropdown in build_html."""

    def test_build_html_contains_region_dropdown(self, df):
        html = build_html(df)
        assert 'id="rFilter"' in html

    def test_build_html_contains_all_region_options(self, df):
        html = build_html(df)
        for region in ["All Regions", "East", "West", "South", "Midwest"]:
            assert f'value="{region}"' in html

    def test_build_html_contains_quarter_dropdown(self, df):
        html = build_html(df)
        assert 'id="qFilter"' in html

    def test_build_html_initialises_with_all_regions(self, df):
        html = build_html(df)
        assert 'applyFilter("Full Year", "All Regions")' in html

    def test_region_filter_data_nested_in_html(self, df):
        html = build_html(df)
        # Extract the DATA JSON object from the script tag
        match = re.search(r"const DATA = (\{.*?\});\n", html, re.DOTALL)
        assert match, "DATA object not found in HTML"
        data = json.loads(match.group(1))
        # Top-level keys should be quarters
        assert "Full Year" in data
        # Each quarter should have region keys
        assert "All Regions" in data["Full Year"]
        assert "East" in data["Full Year"]
        # Each region entry should have KPI and chart keys
        entry = data["Full Year"]["All Regions"]
        for key in ("total_revenue", "total_orders", "avg_order", "top_region",
                    "region", "monthly", "category", "top_products"):
            assert key in entry, f"Missing key: {key}"

    def test_all_regions_restores_full_revenue(self, df):
        html = build_html(df)
        match = re.search(r"const DATA = (\{.*?\});\n", html, re.DOTALL)
        data = json.loads(match.group(1))
        all_rev_str = data["Full Year"]["All Regions"]["total_revenue"]
        # Should match the full-year total revenue
        expected = f"${df['revenue'].sum():,.0f}"
        assert all_rev_str == expected

    def test_single_region_filter_reduces_revenue(self, df):
        html = build_html(df)
        match = re.search(r"const DATA = (\{.*?\});\n", html, re.DOTALL)
        data = json.loads(match.group(1))
        full_rev_str = data["Full Year"]["All Regions"]["total_revenue"]
        east_rev_str = data["Full Year"]["East"]["total_revenue"]
        # East revenue should be less than total
        full_rev = float(full_rev_str.replace("$", "").replace(",", ""))
        east_rev = float(east_rev_str.replace("$", "").replace(",", ""))
        assert east_rev < full_rev
