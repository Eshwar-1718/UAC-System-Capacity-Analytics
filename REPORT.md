# System Capacity & Care Load Analytics for Unaccompanied Children
## Research Report

### Executive purpose
This analysis converts daily operational counts into a capacity-monitoring framework for the UAC care pipeline. The objective is to help decision-makers identify care load, inflow/outflow imbalance, volatility, backlog pressure, and emerging capacity strain.

### Data and preparation
The supplied dataset contains 720 valid daily observations from 2023-01-12 through 2025-12-21. After removing 450 completely blank trailing rows, dates were parsed and ordered chronologically and comma-formatted HHS counts were converted to numeric values. The calendar check found 355 dates without observations; these were retained as reporting gaps rather than interpreted as zero-demand days.

Validation flags were created for transfers greater than the reported same-day CBP custody count and discharges greater than same-day HHS care. These flags are transparency checks, not automatic declarations of error, because stock and flow variables may use different operational reporting cutoffs.

### Analytical framework
**Total System Load** measures simultaneous responsibility across CBP and HHS.  
**Net Daily Intake** measures daily HHS-directed inflow minus HHS discharges.  
**Discharge Offset Ratio** measures the extent to which discharges relieve transfer pressure.  
**Volatility Index** is the 30-day rolling coefficient of variation of total system load.  
**Backlog Accumulation** cumulatively tracks positive net-intake days.  
Seven- and fourteen-day moving averages smooth daily noise and help distinguish sustained pressure from short spikes.

### Key findings
- The latest observed total system load is **2,502 children**.
- The latest observed HHS care population is **2,484 children**, compared with **18 in CBP custody**.
- The highest observed total system load was **11,762 children on 2023-12-20**.
- Average net daily intake across the dataset was **-44.74 children per day**.
- The median discharge offset ratio was **127.80%**.
- The 30-day forecast validation produced **MAE 75.36** and **RMSE 90.01**.

### Forecasting methodology
A trend-based exponential smoothing model was selected as an interpretable baseline for daily HHS care levels. The final 30 observed days were held out for back-testing. The model was then refit on the complete daily HHS-care series and used to generate a 30-day forecast. For production use, the model should be retrained regularly and compared with seasonal and regression-based alternatives as more data accumulates.

### Operational recommendations
1. Use the 7-day net-intake average as an early-warning signal rather than reacting to single-day spikes.
2. Escalate staffing and shelter contingency planning when sustained positive net intake coincides with rising total-system load.
3. Track discharge offset ratio jointly with absolute discharge volume; a high ratio during low transfer volume may not represent strong system relief.
4. Investigate reporting-cutoff differences before treating validation flags as data errors.
5. Use forecast ranges and scenario planning before committing irreversible capacity decisions.
6. Establish green/amber/red thresholds based on historical percentiles and physical bed/staff capacity.

### Limitations
This dataset contains aggregate counts and no explicit bed capacity, staffing capacity, facility-level geography, demographic mix, or causal drivers. Therefore, “capacity strain” is inferred from relative load and flow imbalance rather than directly measured against a known maximum capacity. The analysis is decision support and should be combined with operational capacity data before deployment.

### Conclusion
The project provides a reproducible analytical framework for converting daily UAC pipeline counts into actionable indicators. The strongest practical use is as an early-warning and situational-awareness layer: monitor total load, sustained net intake, rolling volatility, discharge relief, and near-term forecast together rather than relying on any single metric.
