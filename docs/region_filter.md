# Region Filter Enhancement — Implementation Guide

## Overview

The region filter is a dynamic dropdown added to the retail sales dashboard that allows users to narrow all KPI cards and charts to a single geographic region — **East**, **West**, **South**, or **Midwest** — or view aggregated data across **All Regions**. It works in combination with the existing quarter filter so that analysts can, for example, examine *Q2 revenue for the West region* in a single click without regenerating the dashboard.

---

## Feature Purpose

Retail operations are often evaluated at a regional level: different markets have distinct product mixes, seasonal patterns, and performance benchmarks. Before this enhancement, the dashboard displayed company-wide figures only, forcing analysts to run separate scripts or export filtered CSVs to answer region-specific questions. The region filter eliminates that friction by embedding every region/quarter combination in the generated HTML, making the drill-down instant and server-free.

---

## How the Region Filter Works

### Build time (Python — `dashboard.py`)

`build_html()` iterates over all **5 quarter values** (`Full Year`, `Q1`–`Q4`) and all **5 region values** (`All Regions`, `East`, `West`, `South`, `Midwest`) — both lists are currently fixed constants in `build_html()`; the values shown here reflect the 2024 dataset and should be updated if the data source changes. This produces a **25-entry nested dictionary**:

```
chart_data[quarter][region] = {
    "region":        <Plotly JSON>,   # Revenue-by-region bar chart
    "monthly":       <Plotly JSON>,   # Monthly revenue trend line chart
    "category":      <Plotly JSON>,   # Revenue-by-category donut pie
    "top_products":  <Plotly JSON>,   # Top 10 products bar chart
    "total_revenue": "$xxx,xxx",      # Formatted KPI string
    "total_orders":  "xxx",           # Formatted KPI string
    "avg_order":     "$x,xxx",        # Formatted KPI string
    "top_region":    "<region name>", # KPI string
}
```

For any subset with zero rows (e.g., a quarter where a region had no transactions), placeholder empty figures are stored so the JavaScript never encounters missing keys.

The entire `chart_data` dictionary is serialised with `json.dumps()` and embedded as a JavaScript constant (`const DATA = ...`) inside the `<script>` block of the output HTML.

### Run time (JavaScript — embedded in `dashboard.html`)

When the user changes either dropdown, the `applyFilter(quarter, region)` function:

1. Looks up `DATA[quarter][region]` — an O(1) dictionary access with no network call.
2. Re-renders the **four KPI cards** (Total Revenue, Transactions, Avg Transaction, Top Region) by replacing the inner HTML of `#kpiRow`.
3. Calls `Plotly.react()` on each of the **four chart containers** to swap in the new traces and layout without a full page reload:
   - `#chartRegion` — Revenue by Region bar chart
   - `#chartMonthly` — Monthly Revenue Trend line chart
   - `#chartCategory` — Revenue by Category donut pie
   - `#chartTopProducts` — Top 10 Products horizontal bar chart
4. Updates the text in `#filterLabel` to confirm the active selection (e.g., *"Showing Q2 2024 · West"*).

The page initialises to `applyFilter("Full Year", "All Regions")` on load, so the dashboard is always fully populated when first opened.

---

## Dashboard Components Updated Dynamically

| Component | Element ID | Update Mechanism |
|-----------|-----------|-----------------|
| KPI — Total Revenue | `#kpiRow` | Inner HTML replacement |
| KPI — Transactions | `#kpiRow` | Inner HTML replacement |
| KPI — Avg Transaction | `#kpiRow` | Inner HTML replacement |
| KPI — Top Region | `#kpiRow` | Inner HTML replacement |
| Revenue by Region chart | `#chartRegion` | `Plotly.react()` |
| Monthly Revenue Trend chart | `#chartMonthly` | `Plotly.react()` |
| Revenue by Category chart | `#chartCategory` | `Plotly.react()` |
| Top 10 Products chart | `#chartTopProducts` | `Plotly.react()` |
| Active filter label | `#filterLabel` | `textContent` assignment |

---

## Changes to `dashboard.py`

| Area | Change |
|------|--------|
| `build_html()` — data preparation | Added an inner loop over `regions = ["All Regions", "East", "West", "South", "Midwest"]`. For each `(quarter, region)` pair the DataFrame is filtered with `q_subset[q_subset["region"] == r]` (or left unfiltered for `"All Regions"`), and the four chart figures plus four KPI values are computed from the subset. |
| `build_html()` — empty-data guard | Added an `if subset.empty` branch that stores placeholder empty `go.Figure()` objects and zero-value KPI strings, preventing JavaScript from encountering undefined keys. |
| `build_html()` — HTML filter bar | Added a second `<select>` element (`id="rFilter"`) with one `<option>` per region. Both dropdowns call `applyFilter()`, passing the current value of the *other* dropdown as well as their own. |
| `build_html()` — JavaScript | Updated `applyFilter()` to accept a `region` argument in addition to `quarter`, and to look up `DATA[quarter][region]` instead of `DATA[quarter]`. |
| `build_html()` — initialisation call | Updated `applyFilter("Full Year", "All Regions")` to pass both arguments on page load. |

No new top-level functions were required; all logic is contained within `build_html()`. The existing chart-builder functions (`build_region_bar`, `build_monthly_line`, `build_category_pie`, `build_top_products`) were not modified — their signatures already accepted an arbitrary `pd.DataFrame`, so passing a region-filtered subset to them required no changes to those functions.

---

## Changes to `tests/test_dashboard.py`

A new test class `TestRegionFilter` was added (seven tests):

| Test | What It Validates |
|------|--------------------|
| `test_build_html_contains_region_dropdown` | The rendered HTML includes `id="rFilter"`. |
| `test_build_html_contains_all_region_options` | All five region option values appear in the HTML. |
| `test_build_html_contains_quarter_dropdown` | The rendered HTML still includes `id="qFilter"` (regression guard). |
| `test_build_html_initialises_with_all_regions` | The on-load call is `applyFilter("Full Year", "All Regions")`. |
| `test_region_filter_data_nested_in_html` | The embedded `DATA` JSON is valid, contains the expected quarter/region nesting, and each entry carries all eight required keys. |
| `test_all_regions_restores_full_revenue` | `DATA["Full Year"]["All Regions"]["total_revenue"]` matches the sum of all rows in the CSV. |
| `test_single_region_filter_reduces_revenue` | `DATA["Full Year"]["East"]["total_revenue"]` is strictly less than the full-year total, confirming that the region sub-filter actually reduces scope. |

---

## Business Usability and Decision-Making Impact

| Business Need | How the Feature Addresses It |
|--------------|------------------------------|
| **Regional performance benchmarking** | Sales managers can compare KPIs across East, West, South, and Midwest without building separate reports. |
| **Quarterly drill-down by geography** | Filtering to *Q4 / West*, for example, immediately reveals whether holiday-season sales in the Western market met targets. |
| **Anomaly detection** | A region whose monthly trend diverges from the company-wide pattern becomes visible the moment the analyst selects that region. |
| **Self-service analysis** | Because all data is embedded in a single HTML file, the dashboard can be emailed or shared on a network drive and requires no server or database connection to operate interactively. |
| **Reduced manual work** | Analysts no longer need to export filtered CSVs or re-run Python scripts to answer region-specific questions; the answer is one dropdown selection away. |
