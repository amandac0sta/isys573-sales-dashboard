# ISYS 573 Sales Dashboard
### AugOps Demo · Generative AI and LLMs for Business · SFSU

An interactive retail sales dashboard built entirely in Python — reads `data/sales.csv`
and generates a single self-contained HTML file with drill-down charts.

This repo is the live demo for **Slides 15–17: GitHub Copilot 2025 — The Full Agentic Workflow**.
It demonstrates the AugOps development loop using both GitHub Copilot and Claude as agents.

---

## Quick Start

```bash
git clone https://github.com/samgill172/isys573-sales-dashboard
cd isys573-sales-dashboard
pip install -r requirements.txt
python dashboard.py
open dashboard.html   # macOS
# or: start dashboard.html  (Windows)
```

## What the Dashboard Shows

| Chart | Description |
|-------|-------------|
| Revenue by Region | Bar chart — West / East / South / Midwest |
| Monthly Trend | Line chart — Jan–Dec revenue |
| Category Breakdown | Donut pie — 6 product categories |
| Top 10 Products | Horizontal bar — best sellers by revenue |
| **Quarter Filter** | Dropdown — Full Year / Q1 / Q2 / Q3 / Q4 |
| **Region Filter** | Dropdown — All Regions / East / West / South / Midwest |

KPI cards show: Total Revenue · Transactions · Avg Transaction · Top Region

> **Implementation details:** See [`docs/region_filter.md`](docs/region_filter.md) for a full explanation of how the region filter works, which components it updates, and the business rationale behind the feature.

## Running Tests

```bash
pytest tests/ -v
```

## The AugOps 5-Step Demo (Slide 15)

| Step | Action |
|------|--------|
| 01 `copilot-instructions.md` | Already committed. Copilot reads it on every task. |
| 02 Agent Mode | Prompt: *"Build the sales dashboard from data/sales.csv with region bar, monthly line, category pie, and top products bar. Output to dashboard.html."* |
| 03 MCP Integration | Create Issue #1 below using GitHub MCP from chat. |
| 04 Coding Agent | Assign Issue #1 to @copilot. Watch it work in the background. |
| 05 Review & Merge | Review the PR diff, comment `@copilot add a summary stats table`, merge. |

---

## Issue #1 — Assign to @copilot (GitHub Coding Agent · A2 Amplify)

> **Title:** Add sales rep leaderboard section to dashboard
>
> **Description:**
> Add a new section below the existing charts showing a sales rep performance leaderboard.
>
> **Acceptance Criteria:**
> - [ ] Horizontal bar chart showing total revenue per sales rep, sorted descending
> - [ ] Chart respects the quarter filter (updates when dropdown changes)
> - [ ] New `build_rep_leaderboard(df)` function in `dashboard.py`
> - [ ] At least 3 pytest tests for the new function in `tests/test_dashboard.py`
> - [ ] All existing tests still pass
>
> **Notes:**
> - Follow existing code style (type hints, docstrings, `pathlib.Path`)
> - Do not modify `data/sales.csv`
> - Run `pytest tests/ -v` before opening the PR

---

## Issue #2 — Assign to @claude (Claude Agent · A4 Adapt)

> **Title:** Generate data dictionary and onboarding guide for the sales dataset
>
> **Description:**
> New team members and students need to understand the dataset before they can contribute.
> Create two Markdown documents that serve as institutional knowledge for the project.
>
> **Deliverable 1 — `docs/data_dictionary.md`**
> A structured data dictionary table with one row per column containing:
> - Column name, data type, description, example value, constraints/business rules
>
> **Deliverable 2 — `docs/onboarding.md`**
> A short onboarding guide (300–400 words) covering:
> - What the dataset represents and where it comes from
> - How to run the dashboard and how the quarter filter works
> - How to add a new chart (step-by-step, referencing existing functions)
> - How to run the test suite and what each test class covers
>
> **Acceptance Criteria:**
> - [ ] `docs/data_dictionary.md` exists with complete table for all 10 columns
> - [ ] `docs/onboarding.md` exists and covers all four topics above
> - [ ] All column descriptions verified against `data/sales.csv` — no invented values
> - [ ] Writing is clear and appropriate for graduate IS students
> - [ ] No code changes — documentation only, new files in `docs/` only
>
> **Notes:**
> - Read `data/sales.csv` to verify example values are real
> - Read `dashboard.py` to accurately describe how each chart function works
> - Read `tests/test_dashboard.py` to accurately describe what each test class covers
> - Do not modify any existing files

---

*Dataset: 500 synthetic retail transactions · 2024 · 4 regions · 6 categories · 10 sales reps*
