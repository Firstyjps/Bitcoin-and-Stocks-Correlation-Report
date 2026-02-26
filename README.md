# Bitcoin-and-Stocks-Correlation-Report

A Streamlit dashboard + research workflow for analyzing **Bitcoin correlation with major asset classes**, focusing on:
- **BTC vs Nasdaq (QQQ)**
- **BTC vs S&P 500 (SPY)**
- **BTC vs Gold**
- (Optional add-on) **SET50** as an extra comparison asset

This project is built for generating **rolling correlation (e.g., 30-day window)** and visualizing how correlations change over time.

## Live Results (Streamlit App)
You can view the dashboard and results here:
**https://firstyjps.streamlit.app**

## Features
- Rolling correlation analysis (e.g., 30 trading days)
- Timeframe filtering (e.g., 1Y / 3Y / 5Y / All-time depending on data)
- Clean visualization for correlation + price trends
- Export-ready workflow for turning charts into a report (PDF/Word)

## Project Structure
- `dashboard.py` — Streamlit app (main dashboard)
- `requirements.txt` — required Python packages
- `test.ipynb` — notebook experiments / drafts
- `test.py` — quick testing script(s)
- `README.md` — project overview

## How to Run Locally
1) Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate  
