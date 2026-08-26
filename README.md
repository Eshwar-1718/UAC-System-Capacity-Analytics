# System Capacity & Care Load Analytics for Unaccompanied Children

## Project Overview

This project analyzes the operational capacity and care load of the Unaccompanied Alien Children (UAC) care system.

The project uses daily operational data to monitor the movement of children through the care pipeline, including:

- CBP custody
- Transfers into HHS care
- Active HHS care load
- Discharges and sponsor placements
- Total system capacity
- Intake pressure and backlog accumulation
- High-pressure operational periods
- Short-term HHS care forecasting

An interactive Streamlit dashboard was developed to transform daily operational data into decision-support insights for healthcare and capacity planning.

---

## Problem Statement

The UAC care system functions as a dynamic care pipeline. Sudden increases in child arrivals can create pressure on:

- Shelter capacity
- Healthcare staffing
- Medical and psychological support
- Sponsor placement operations

Without a centralized analytical framework, capacity management can become reactive.

This project provides an analytical framework to continuously assess:

- Total care system load
- Balance between inflow and outflow
- Capacity stress and relief periods
- Backlog risk
- Sustainability of care delivery
- Near-term operational demand

---

## Project Objectives

### Primary Objectives

- Quantify daily and cumulative care load across CBP and HHS
- Identify periods of capacity strain and relief
- Analyze the balance between intake, transfers, and discharges

### Secondary Objectives

- Support healthcare staffing and shelter planning
- Improve situational awareness for decision-makers
- Enable data-driven humanitarian response evaluation
- Forecast near-term HHS care demand

---

## Dataset

The dataset contains daily operational records from 2023 to 2025.

### Key Variables

| Column | Description |
|---|---|
| Date | Reporting date |
| Children apprehended and placed in CBP custody | Daily intake volume |
| Children in CBP custody | Active CBP care load |
| Children transferred out of CBP custody | Flow into HHS care |
| Children in HHS Care | Active HHS care load |
| Children discharged from HHS Care | Successful sponsor placements |

The data is cleaned and transformed into a structured daily analytical dataset.

---

## Derived Healthcare Capacity Metrics

### Total System Load

```text
CBP Custody + HHS Care