import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="UAC Care Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f7f9fc;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* SECTION HEADERS */

.section-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: #102a43;
    margin-top: 1.6rem;
    margin-bottom: 0.35rem;
}

.section-subtitle {
    color: #64748b;
    margin-bottom: 1rem;
}

/* KPI CARDS */

.metric-card {
    background: white;
    padding: 1.2rem;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.06);
    min-height: 150px;
}

.metric-label {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 600;
}

.metric-value {
    color: #102a43;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 0.5rem;
}

.metric-description {
    color: #94a3b8;
    font-size: 0.75rem;
    margin-top: 0.4rem;
    line-height: 1.4;
}

/* INSIGHT CARDS */

.insight-card {
    background: white;
    padding: 1.2rem;
    border-radius: 12px;
    border-left: 5px solid #1f77b4;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05);
    margin-bottom: 0.8rem;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent

DATA_PATH = ROOT / "data" / "processed_uac_daily.csv"
FORECAST_PATH = ROOT / "outputs" / "hhs_care_30_day_forecast.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["Date"]
    )

    forecast = pd.read_csv(
        FORECAST_PATH,
        parse_dates=["Date"]
    )

    df = df.sort_values("Date").reset_index(drop=True)
    forecast = forecast.sort_values("Date").reset_index(drop=True)

    return df, forecast


df, forecast = load_data()


# ============================================================
# DATA PREPARATION
# ============================================================

if "Total_System_Load" not in df.columns:

    df["Total_System_Load"] = (
        df["CBP_Custody"]
        +
        df["HHS_Care"]
    )


if "Net_Daily_Intake" not in df.columns:

    df["Net_Daily_Intake"] = (
        df["CBP_Transferred"]
        -
        df["HHS_Discharged"]
    )


if "System_Load_7D_MA" not in df.columns:

    df["System_Load_7D_MA"] = (
        df["Total_System_Load"]
        .rolling(7, min_periods=1)
        .mean()
    )


if "System_Load_14D_MA" not in df.columns:

    df["System_Load_14D_MA"] = (
        df["Total_System_Load"]
        .rolling(14, min_periods=1)
        .mean()
    )


if "Care_Load_Growth_Rate" not in df.columns:

    df["Care_Load_Growth_Rate"] = (
        df["Total_System_Load"]
        .pct_change()
        * 100
    )


if "Backlog_Accumulation" not in df.columns:

    df["Backlog_Accumulation"] = (
        df["Net_Daily_Intake"]
        .clip(lower=0)
        .cumsum()
    )


if "Backlog_Accumulation_Rate" not in df.columns:

    df["Backlog_Accumulation_Rate"] = (
        df["Net_Daily_Intake"]
        .clip(lower=0)
        .rolling(7, min_periods=1)
        .mean()
    )


if "Care_Load_Volatility_Index" not in df.columns:

    daily_change = (
        df["Total_System_Load"]
        .pct_change()
        * 100
    )

    df["Care_Load_Volatility_Index"] = (
        daily_change
        .rolling(7, min_periods=2)
        .std()
    )


if "Discharge_Offset_Ratio" not in df.columns:

    df["Discharge_Offset_Ratio"] = np.where(
        df["CBP_Transferred"] > 0,
        (
            df["HHS_Discharged"]
            /
            df["CBP_Transferred"]
        )
        * 100,
        np.nan
    )


if "Flag_Transfer_GT_CBP_Custody" not in df.columns:

    df["Flag_Transfer_GT_CBP_Custody"] = (
        df["CBP_Transferred"]
        >
        df["CBP_Custody"]
    )


if "Flag_Discharge_GT_HHS_Care" not in df.columns:

    df["Flag_Discharge_GT_HHS_Care"] = (
        df["HHS_Discharged"]
        >
        df["HHS_Care"]
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📊 UAC Intelligence")

    st.caption("Healthcare Capacity Analytics")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Executive Overview",
            "📈 System Capacity",
            "🔄 Flow & Backlog",
            "🔮 Forecast & Risk",
            "🔎 Data Quality"
        ]
    )

    st.divider()

    st.subheader("Filters")

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    date_range = st.date_input(
        "Analysis Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    st.divider()

    granularity = st.selectbox(
        "Time Granularity",
        [
            "Daily",
            "Weekly",
            "Monthly"
        ]
    )

    st.divider()

    st.caption(
        "Decision-support analytics for monitoring "
        "care-system capacity and operational pressure."
    )


# ============================================================
# FILTER DATA
# ============================================================

if len(date_range) == 2:

    start_date = date_range[0]
    end_date = date_range[1]

else:

    start_date = min_date
    end_date = max_date


filtered_df = df[
    (df["Date"].dt.date >= start_date)
    &
    (df["Date"].dt.date <= end_date)
].copy()


if filtered_df.empty:

    st.warning(
        "No data is available for the selected date range."
    )

    st.stop()


# ============================================================
# TIME GRANULARITY FUNCTION
# ============================================================

def aggregate_data(data, level):

    numeric_columns = data.select_dtypes(
        include=np.number
    ).columns.tolist()

    if level == "Daily":

        return data.copy()

    temp = data.copy()

    temp = temp.set_index("Date")

    if level == "Weekly":

        result = (
            temp[numeric_columns]
            .resample("W")
            .mean()
            .reset_index()
        )

    else:

        result = (
            temp[numeric_columns]
            .resample("ME")
            .mean()
            .reset_index()
        )

    return result


display_df = aggregate_data(
    filtered_df,
    granularity
)


# ============================================================
# COMMON CALCULATIONS
# ============================================================

latest = filtered_df.iloc[-1]

peak_row = filtered_df.loc[
    filtered_df["Total_System_Load"].idxmax()
]

average_net_intake = (
    filtered_df["Net_Daily_Intake"]
    .mean()
)

discharge_offset = (
    filtered_df["Discharge_Offset_Ratio"]
    .median()
)

latest_growth = (
    latest["Care_Load_Growth_Rate"]
)

if pd.isna(latest_growth):

    latest_growth = 0


latest_volatility = (
    latest["Care_Load_Volatility_Index"]
)

if pd.isna(latest_volatility):

    latest_volatility = 0


latest_backlog_rate = (
    latest["Backlog_Accumulation_Rate"]
)

if pd.isna(latest_backlog_rate):

    latest_backlog_rate = 0


# ============================================================
# PRESSURE SCORE
# ============================================================

load_score = min(
    (
        latest["Total_System_Load"]
        /
        df["Total_System_Load"].max()
    )
    *
    100,
    100
)


max_positive_net_intake = (
    df["Net_Daily_Intake"]
    .clip(lower=0)
    .max()
)


if max_positive_net_intake > 0:

    net_intake_score = min(
        (
            max(
                latest["Net_Daily_Intake"],
                0
            )
            /
            max_positive_net_intake
        )
        *
        100,
        100
    )

else:

    net_intake_score = 0


max_volatility = (
    df["Care_Load_Volatility_Index"]
    .max()
)


if (
    pd.notna(max_volatility)
    and
    max_volatility > 0
):

    volatility_score = min(
        (
            latest_volatility
            /
            max_volatility
        )
        *
        100,
        100
    )

else:

    volatility_score = 0


pressure_score = round(
    (
        load_score * 0.50
        +
        net_intake_score * 0.30
        +
        volatility_score * 0.20
    ),
    1
)


# ============================================================
# PRESSURE CLASSIFICATION
# ============================================================

if pressure_score < 35:

    pressure_status = "LOW"

elif pressure_score < 65:

    pressure_status = "MODERATE"

else:

    pressure_status = "HIGH"


# ============================================================
# STRAIN ANALYSIS
# ============================================================

strain_df = filtered_df.copy()


def calculate_pressure_scores(data):

    result = data.copy()

    max_load = result[
        "Total_System_Load"
    ].max()

    max_net = (
        result[
            "Net_Daily_Intake"
        ]
        .clip(lower=0)
        .max()
    )

    max_vol = result[
        "Care_Load_Volatility_Index"
    ].max()


    if max_load > 0:

        result["Load_Score"] = (
            result["Total_System_Load"]
            /
            max_load
            *
            100
        )

    else:

        result["Load_Score"] = 0


    if (
        pd.notna(max_net)
        and
        max_net > 0
    ):

        result["Net_Intake_Score"] = (
            result[
                "Net_Daily_Intake"
            ]
            .clip(lower=0)
            /
            max_net
            *
            100
        )

    else:

        result["Net_Intake_Score"] = 0


    if (
        pd.notna(max_vol)
        and
        max_vol > 0
    ):

        result["Volatility_Score"] = (
            result[
                "Care_Load_Volatility_Index"
            ]
            .fillna(0)
            /
            max_vol
            *
            100
        )

    else:

        result["Volatility_Score"] = 0


    result["Pressure_Score"] = (
        result["Load_Score"] * 0.50
        +
        result["Net_Intake_Score"] * 0.30
        +
        result["Volatility_Score"] * 0.20
    )

    return result


strain_df = calculate_pressure_scores(
    strain_df
)


strain_df["High_Pressure"] = (
    strain_df["Pressure_Score"]
    >= 65
)


strain_df["Strain_Group"] = (
    strain_df["High_Pressure"]
    !=
    strain_df["High_Pressure"].shift()
).cumsum()


high_pressure_periods = []


for _, group in strain_df.groupby(
    "Strain_Group"
):

    if group["High_Pressure"].iloc[0]:

        high_pressure_periods.append(
            {
                "Start Date":
                    group["Date"].min(),

                "End Date":
                    group["Date"].max(),

                "Duration (Days)":
                    len(group),

                "Peak Pressure":
                    round(
                        group[
                            "Pressure_Score"
                        ].max(),
                        1
                    )
            }
        )


strain_periods_df = pd.DataFrame(
    high_pressure_periods
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def section_header(title, subtitle):

    html = f"""
    <div class="section-title">{title}</div>
    <div class="section-subtitle">{subtitle}</div>
    """

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def metric_card(title, value, description):

    html = f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-description">{description}</div>
    </div>
    """

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "🏠 Executive Overview":

    section_header(
        "Executive System Snapshot",
        "High-level operational indicators for the selected analysis period."
    )


    row1_col1, row1_col2, row1_col3, row1_col4 = (
        st.columns(4)
    )


    with row1_col1:

        metric_card(
            "Children Under Care",
            f"{latest['Total_System_Load']:,.0f}",
            "Combined CBP and HHS active care load"
        )


    with row1_col2:

        metric_card(
            "Net Intake Pressure",
            f"{average_net_intake:,.1f}",
            "Average daily transfer minus discharge balance"
        )


    with row1_col3:

        metric_card(
            "Peak System Load",
            f"{peak_row['Total_System_Load']:,.0f}",
            "Highest recorded care-system load"
        )


    with row1_col4:

        metric_card(
            "Discharge Offset",
            f"{discharge_offset:,.1f}%",
            "Median ability of discharges to offset transfers"
        )


    st.markdown("<br>", unsafe_allow_html=True)


    row2_col1, row2_col2, row2_col3 = (
        st.columns(3)
    )


    with row2_col1:

        metric_card(
            "Care Load Growth",
            f"{latest_growth:+.2f}%",
            "Latest day-over-day system load change"
        )


    with row2_col2:

        metric_card(
            "Care Load Volatility",
            f"{latest_volatility:.2f}",
            "Seven-day variation in system load movement"
        )


    with row2_col3:

        metric_card(
            "Backlog Accumulation Rate",
            f"{latest_backlog_rate:,.1f}",
            "Seven-day average positive intake pressure"
        )


    st.markdown("<br>", unsafe_allow_html=True)


    section_header(
        "Operational Pressure Assessment",
        "Composite risk indicator based on current load, intake pressure and volatility."
    )


    left, right = st.columns(
        [1, 2]
    )


    with left:

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=pressure_score,
                number={
                    "suffix": " / 100"
                },
                title={
                    "text":
                        f"Pressure Level: {pressure_status}"
                },
                gauge={
                    "axis": {
                        "range": [0, 100]
                    },

                    "bar": {
                        "color": "#1f77b4"
                    },

                    "steps": [
                        {
                            "range": [0, 35],
                            "color": "#d9f0d3"
                        },
                        {
                            "range": [35, 65],
                            "color": "#fff2cc"
                        },
                        {
                            "range": [65, 100],
                            "color": "#f4cccc"
                        }
                    ]
                }
            )
        )


        fig.update_layout(
            height=330,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with right:

        assessment_html = f"""
        <div class="insight-card">
            <b>Current System Assessment</b>
            <br><br>

            The current composite pressure score is
            <b>{pressure_score}/100</b>,
            classified as <b>{pressure_status}</b>.

            <br><br>

            The indicator combines current care-system load,
            positive intake pressure and recent volatility to provide
            a simple operational early-warning signal.
        </div>
        """


        st.markdown(
            assessment_html,
            unsafe_allow_html=True
        )


        if average_net_intake > 0:

            insight = (
                "⚠️ Average inflow pressure exceeds the "
                "discharge response during the selected period."
            )

        else:

            insight = (
                "✅ Discharge activity is helping offset "
                "incoming transfer pressure."
            )


        insight_html = f"""
        <div class="insight-card">
            <b>Automated Insight</b>
            <br><br>
            {insight}
        </div>
        """


        st.markdown(
            insight_html,
            unsafe_allow_html=True
        )


    section_header(
        "System Load Trend",
        "Explore care-system load using your selected time granularity and metrics."
    )


    metric_options = {
        "Total System Load":
            "Total_System_Load",

        "CBP Custody":
            "CBP_Custody",

        "HHS Care":
            "HHS_Care",

        "7-Day Average":
            "System_Load_7D_MA",

        "14-Day Average":
            "System_Load_14D_MA"
    }


    selected_metric_names = st.multiselect(
        "Select Metrics",
        options=list(metric_options.keys()),
        default=[
            "Total System Load",
            "7-Day Average",
            "14-Day Average"
        ]
    )


    selected_columns = [
        metric_options[name]
        for name in selected_metric_names
    ]


    if selected_columns:

        fig = px.line(
            display_df,
            x="Date",
            y=selected_columns,
            labels={
                "value": "Children",
                "variable": "Metric"
            }
        )


        fig.update_layout(
            legend_title_text="",
            hovermode="x unified",
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Please select at least one metric."
        )


    section_header(
        "Growth and Volatility",
        "Monitor changes in care-system load and short-term operational instability."
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.line(
            display_df,
            x="Date",
            y="Care_Load_Growth_Rate",
            labels={
                "Care_Load_Growth_Rate":
                    "Growth Rate (%)"
            }
        )


        fig.add_hline(
            y=0,
            line_dash="dash"
        )


        fig.update_layout(
            title="Care Load Growth Rate",
            height=400
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.line(
            display_df,
            x="Date",
            y="Care_Load_Volatility_Index",
            labels={
                "Care_Load_Volatility_Index":
                    "Volatility Index"
            }
        )


        fig.update_layout(
            title="Care Load Volatility",
            height=400
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    section_header(
        "Key Decision Insights",
        "Automatically generated observations from the selected data."
    )


    insight1, insight2, insight3 = st.columns(3)


    with insight1:

        st.info(
            f"""
**Peak Load**

The highest observed system load was
**{peak_row['Total_System_Load']:,.0f} children**.

This occurred on
**{peak_row['Date'].strftime('%d %B %Y')}**.
"""
        )


    with insight2:

        trend_difference = (
            latest["System_Load_7D_MA"]
            -
            latest["System_Load_14D_MA"]
        )


        if trend_difference > 0:

            trend_message = (
                "Short-term pressure is increasing relative "
                "to the longer-term trend."
            )

        else:

            trend_message = (
                "Short-term load is below or near the "
                "longer-term trend."
            )


        st.success(
            f"""
**Trend Signal**

{trend_message}
"""
        )


    with insight3:

        if discharge_offset >= 100:

            discharge_message = (
                "Discharges are generally offsetting or "
                "exceeding transfer pressure."
            )

        else:

            discharge_message = (
                "Discharge activity is not fully offsetting "
                "transfer pressure."
            )


        st.warning(
            f"""
**Discharge Performance**

{discharge_message}
"""
        )


# ============================================================
# SYSTEM CAPACITY PAGE
# ============================================================

elif page == "📈 System Capacity":

    section_header(
        "CBP vs HHS Care Load",
        "Compare responsibility across the two major stages of the care pipeline."
    )


    fig = px.area(
        display_df,
        x="Date",
        y=[
            "CBP_Custody",
            "HHS_Care"
        ],
        labels={
            "value": "Children",
            "variable": "Care System"
        }
    )


    fig.update_layout(
        hovermode="x unified",
        height=500
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    section_header(
        "Care Load Distribution",
        "Current distribution of children across CBP and HHS care systems."
    )


    col1, col2 = st.columns(
        [1, 2]
    )


    with col1:

        pie_data = pd.DataFrame(
            {
                "System": [
                    "CBP Custody",
                    "HHS Care"
                ],

                "Children": [
                    latest["CBP_Custody"],
                    latest["HHS_Care"]
                ]
            }
        )


        fig = px.pie(
            pie_data,
            values="Children",
            names="System",
            hole=0.6
        )


        fig.update_layout(
            height=400
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        st.dataframe(
            filtered_df[
                [
                    "Date",
                    "CBP_Custody",
                    "HHS_Care",
                    "Total_System_Load"
                ]
            ]
            .sort_values(
                "Total_System_Load",
                ascending=False
            )
            .head(10),
            use_container_width=True
        )


# ============================================================
# FLOW & BACKLOG PAGE
# ============================================================

elif page == "🔄 Flow & Backlog":

    section_header(
        "Care Pipeline Flow",
        "Monitor transfers into HHS care and discharges from the care system."
    )


    fig = px.line(
        display_df,
        x="Date",
        y=[
            "CBP_Transferred",
            "HHS_Discharged"
        ],
        labels={
            "value": "Children",
            "variable": "Flow"
        }
    )


    fig.update_layout(
        hovermode="x unified",
        height=450
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    section_header(
        "Net Intake Pressure",
        "Positive values indicate transfers exceed HHS discharges."
    )


    fig = px.bar(
        display_df,
        x="Date",
        y="Net_Daily_Intake"
    )


    fig.add_hline(
        y=0,
        line_dash="dash"
    )


    fig.update_layout(
        height=400
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    section_header(
        "Backlog Accumulation",
        "Sustained positive net intake indicates increasing care-system pressure."
    )


    fig = px.line(
        display_df,
        x="Date",
        y=[
            "Backlog_Accumulation",
            "Backlog_Accumulation_Rate"
        ],
        labels={
            "value": "Children",
            "variable": "Backlog Metric"
        }
    )


    fig.update_layout(
        height=450,
        hovermode="x unified"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    section_header(
        "Prolonged Capacity Strain Windows",
        "Consecutive periods where the composite pressure score exceeded the high-risk threshold."
    )


    if strain_periods_df.empty:

        st.success(
            "No prolonged high-pressure periods were detected "
            "in the selected analysis period."
        )

    else:

        st.warning(
            f"{len(strain_periods_df)} high-pressure "
            f"period(s) were detected."
        )


        strain_periods_display = (
            strain_periods_df.copy()
        )


        strain_periods_display[
            "Start Date"
        ] = strain_periods_display[
            "Start Date"
        ].dt.strftime(
            "%d %b %Y"
        )


        strain_periods_display[
            "End Date"
        ] = strain_periods_display[
            "End Date"
        ].dt.strftime(
            "%d %b %Y"
        )


        st.dataframe(
            strain_periods_display,
            use_container_width=True
        )


# ============================================================
# FORECAST & RISK PAGE
# ============================================================

elif page == "🔮 Forecast & Risk":

    section_header(
        "30-Day HHS Care Forecast",
        "Near-term operational planning based on historical care trends."
    )


    observed = df[
        ["Date", "HHS_Care"]
    ].rename(
        columns={
            "HHS_Care":
                "Observed HHS Care"
        }
    )


    forecast_data = forecast.copy()


    if "Forecast_HHS_Care" in forecast_data.columns:

        forecast_data = forecast_data.rename(
            columns={
                "Forecast_HHS_Care":
                    "Forecast HHS Care"
            }
        )


    elif "Forecast" in forecast_data.columns:

        forecast_data = forecast_data.rename(
            columns={
                "Forecast":
                    "Forecast HHS Care"
            }
        )


    combined = pd.merge(
        observed,
        forecast_data,
        on="Date",
        how="outer"
    ).sort_values("Date")


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=combined["Date"],
            y=combined[
                "Observed HHS Care"
            ],
            mode="lines",
            name="Observed HHS Care"
        )
    )


    if "Forecast HHS Care" in combined.columns:

        fig.add_trace(
            go.Scatter(
                x=combined["Date"],
                y=combined[
                    "Forecast HHS Care"
                ],
                mode="lines",
                name="30-Day Forecast",
                line=dict(
                    dash="dash"
                )
            )
        )


    fig.update_layout(
        height=500,
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Children"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    forecast_change = None


    if "Forecast HHS Care" in forecast_data.columns:

        forecast_values = (
            forecast_data
            .dropna(
                subset=[
                    "Forecast HHS Care"
                ]
            )
            .sort_values("Date")
        )


        if not forecast_values.empty:

            forecast_start = (
                forecast_values.iloc[0]
            )

            forecast_end = (
                forecast_values.iloc[-1]
            )


            forecast_change = (
                forecast_end[
                    "Forecast HHS Care"
                ]
                -
                forecast_start[
                    "Forecast HHS Care"
                ]
            )


            col1, col2, col3 = (
                st.columns(3)
            )


            with col1:

                st.metric(
                    "Forecast Start",
                    f"{forecast_start['Forecast HHS Care']:,.0f}"
                )


            with col2:

                st.metric(
                    "Forecast End",
                    f"{forecast_end['Forecast HHS Care']:,.0f}"
                )


            with col3:

                st.metric(
                    "Forecast Change",
                    f"{forecast_change:+,.0f}"
                )


    section_header(
        "Forecast Risk Assessment",
        "Interpret the projected direction of HHS care demand."
    )


    if forecast_change is not None:

        if forecast_change > 0:

            st.warning(
                f"""
Projected HHS care demand is expected to increase by
approximately **{forecast_change:,.0f} children** across
the forecast horizon.

Operational planners should monitor shelter capacity,
staffing and sponsor-placement throughput.
"""
            )

        elif forecast_change < 0:

            st.success(
                f"""
Projected HHS care demand is expected to decline by
approximately **{abs(forecast_change):,.0f} children**
across the forecast horizon.

The projected decline may reduce short-term operational
pressure, subject to continued discharge and placement activity.
"""
            )

        else:

            st.info(
                """
Projected HHS care demand is expected to remain
approximately stable across the forecast horizon.
"""
            )


# ============================================================
# DATA QUALITY PAGE
# ============================================================

elif page == "🔎 Data Quality":

    section_header(
        "Data Quality & Validation",
        "Transparent data checks supporting trustworthy healthcare analytics."
    )


    expected_dates = pd.date_range(
        df["Date"].min(),
        df["Date"].max(),
        freq="D"
    )


    actual_dates = pd.DatetimeIndex(
        df["Date"].drop_duplicates()
    )


    missing_dates = expected_dates.difference(
        actual_dates
    )


    duplicate_dates = (
        df["Date"]
        .duplicated()
        .sum()
    )


    missing_values = (
        filtered_df
        .isna()
        .sum()
        .sum()
    )


    transfer_flags = (
        filtered_df[
            "Flag_Transfer_GT_CBP_Custody"
        ]
        .sum()
    )


    discharge_flags = (
        filtered_df[
            "Flag_Discharge_GT_HHS_Care"
        ]
        .sum()
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Missing Dates",
            f"{len(missing_dates):,}"
        )


    with col2:

        st.metric(
            "Duplicate Dates",
            f"{duplicate_dates:,}"
        )


    with col3:

        st.metric(
            "Missing Values",
            f"{missing_values:,}"
        )


    col4, col5, col6 = st.columns(3)


    with col4:

        st.metric(
            "Transfer Validation Flags",
            f"{transfer_flags:,}"
        )


    with col5:

        st.metric(
            "Discharge Validation Flags",
            f"{discharge_flags:,}"
        )


    with col6:

        total_records = len(
            filtered_df
        )


        st.metric(
            "Analysis Records",
            f"{total_records:,}"
        )


    section_header(
        "Data Quality Status",
        "Summary of the validation results."
    )


    if (
        len(missing_dates) == 0
        and
        duplicate_dates == 0
    ):

        st.success(
            "The reporting timeline contains no missing or duplicate dates."
        )

    else:

        st.warning(
            "Timeline completeness issues were detected. "
            "Review the detailed checks below."
        )


    if len(missing_dates) > 0:

        missing_dates_df = pd.DataFrame(
            {
                "Missing Date":
                    missing_dates
            }
        )


        st.subheader(
            "Missing Dates"
        )


        st.dataframe(
            missing_dates_df,
            use_container_width=True
        )


    section_header(
        "Validation Exceptions",
        "Logical exceptions are retained for transparency and reporting review."
    )


    exceptions = filtered_df[
        (
            filtered_df[
                "Flag_Transfer_GT_CBP_Custody"
            ]
        )
        |
        (
            filtered_df[
                "Flag_Discharge_GT_HHS_Care"
            ]
        )
    ]


    if not exceptions.empty:

        st.dataframe(
            exceptions[
                [
                    "Date",
                    "CBP_Custody",
                    "CBP_Transferred",
                    "HHS_Care",
                    "HHS_Discharged",
                    "Flag_Transfer_GT_CBP_Custody",
                    "Flag_Discharge_GT_HHS_Care"
                ]
            ],
            use_container_width=True
        )

    else:

        st.success(
            "No logical validation exceptions were detected "
            "for the selected date range."
        )


    section_header(
        "Download Analysis Data",
        "Export the selected dataset for further analysis."
    )


    csv = filtered_df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    st.download_button(
        label="⬇ Download Filtered Dataset",
        data=csv,
        file_name="uac_capacity_analysis.csv",
        mime="text/csv"
    )