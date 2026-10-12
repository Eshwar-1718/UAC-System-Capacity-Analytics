
# UAC System Capacity Analytics

An interactive Python analytics project for monitoring care-system load, analysing daily inflow and outflow, identifying periods of operational pressure, and forecasting short-term HHS care demand.

## Overview

This project analyses daily operational data from the Unaccompanied Children (UAC) care pipeline involving Customs and Border Protection (CBP) and Health and Human Services (HHS).

The project transforms daily records into analytical metrics, trend indicators, data-quality checks, and a 30-day HHS care forecast.

## Problem Statement

Changes in daily arrivals, transfers, and discharges can affect the number of children in care. Analysing these changes together can help identify sustained increases in care load and potential operational pressure.

This project provides a data-driven framework to explore those patterns and support situational awareness.

## Key Features

- Interactive Streamlit dashboard
- Daily and cumulative care-load analysis
- Intake and discharge trend monitoring
- Net daily intake and discharge offset analysis
- Rolling averages and care-load volatility
- Backlog pressure indicators
- Data-quality validation checks
- 30-day HHS care forecasting
- Forecast evaluation using MAE and RMSE
- CSV-based analytical outputs

## Technology Stack

- **Language:** Python
- **Data analysis:** Pandas, NumPy
- **Dashboard:** Streamlit
- **Forecasting:** Exponential smoothing
- **Data visualisation:** See `app.py` and `requirements.txt` for the libraries used
- **Version control:** Git and GitHub

## Dataset

The analysis covers 720 valid daily observations from January 12, 2023, through December 21, 2025.

The data includes measures related to:

- Children in CBP custody
- Transfers from CBP custody into HHS care
- Children in HHS care
- HHS discharges

Data preparation includes date parsing, numeric conversion, chronological ordering, and validation checks.

Missing reporting dates are treated as gaps, not automatically as zero-demand days.

## Analytical Metrics

| Metric | Purpose |
|---|---|
| Total System Load | Combined active care load across CBP and HHS |
| Net Daily Intake | HHS-directed transfers minus HHS discharges |
| Discharge Offset Ratio | Compares discharges with incoming transfers |
| Care-Load Volatility | Measures variation in recent system load |
| Backlog Accumulation | Tracks cumulative positive net-intake periods |
| Moving Averages | Helps distinguish sustained trends from daily fluctuations |

## Selected Findings

Based on the current analysis report:

- Latest observed combined system load: **2,502**
- Highest observed combined system load: **11,762** on December 20, 2023
- Average net daily intake: **-44.74** children per day
- Median discharge offset ratio: **127.80%**
- 30-day forecast back-test MAE: **75.36**
- 30-day forecast back-test RMSE: **90.01**

These figures describe the analysed dataset and should not be interpreted as live operational statistics.

## Project Files

| File | Description |
|---|---|
| `app.py` | Streamlit dashboard and analytical logic |
| `processed_uac_daily.csv` | Processed daily dataset |
| `hhs_care_30_day_forecast.csv` | Forecast output |
| `data_quality_summary.csv` | Data-quality summary |
| `REPORT.md` | Detailed analytical report |
| `EXECUTIVE_SUMMARY.md` | Summary of findings and recommendations |
| `requirements.txt` | Python dependencies |

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Eshwar-1718/UAC-System-Capacity-Analytics.git
cd UAC-System-Capacity-Analytics
```

### 2. Create a virtual environment

Windows:

```bash
py -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

Open the local URL printed in your terminal.

## Forecasting Approach

The project uses a trend-based exponential smoothing model as an interpretable forecasting baseline.

The final 30 observed days are held out for back-testing. The model is evaluated using:

- **MAE:** Mean Absolute Error
- **RMSE:** Root Mean Squared Error

The reported back-test MAE is 75.36 and RMSE is 90.01. These are historical evaluation results, not a guarantee of future accuracy.

## Limitations

- The dataset contains aggregate counts rather than individual-level records.
- Direct bed-capacity, staffing-capacity, and facility-level denominators are not available.
- Reporting gaps and differences in operational cut-off times can affect interpretation.
- Forecasts are estimates and should be validated against appropriate baselines and newer data.

Therefore, the indicators represent relative operational pressure rather than measured occupancy or confirmed overcrowding.

## Future Improvements

- Add automated data validation and reproducible analysis scripts.
- Compare forecasting models using the same time-based validation period.
- Add automated tests for data transformations and metric calculations.
- Improve dashboard usability and add clear chart explanations.
- Deploy the dashboard so recruiters can explore it online.

## Author

**Eshwar**

- GitHub: [Eshwar-1718](https://github.com/Eshwar-1718)

