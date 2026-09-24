"""
US Provisional Natality Explorer (2025)
Streamlit Dashboard for Undergraduate Business Analytics Students
Integrated Single-File Version
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ---------------------------------------------------------
st.set_page_config(
    page_title="US Provisional Natality Explorer (2025)",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)

STATE_ABBREVIATIONS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


# ---------------------------------------------------------
# DATA LOADING & CACHING
# ---------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """Loads, validates, and cleans the provisional natality dataset."""
    possible_paths = [
        "Provisional_Natality_2025_CDC1.csv",
        "data/Provisional_Natality_2025_CDC1.csv",
    ]

    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        raise FileNotFoundError(
            "Could not locate 'Provisional_Natality_2025_CDC1.csv' in the root or data/ folder."
        )

    df = pd.read_csv(file_path)

    # Data Validation Checks
    expected_columns = {
        "state_of_residence",
        "month",
        "month_code",
        "year_code",
        "sex_of_infant",
        "births",
    }
    missing_cols = expected_columns - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Dataset is missing required columns: {missing_cols}"
        )

    if (df["births"] < 0).any():
        raise ValueError(
            "Data validation error: Negative birth counts detected."
        )

    # Add State Abbreviation column for mapping
    df["state_abbr"] = df["state_of_residence"].map(STATE_ABBREVIATIONS)

    # Chronological month ordering
    df["month"] = pd.Categorical(
        df["month"], categories=MONTH_ORDER, ordered=True
    )
    df = df.sort_values(["month_code", "state_of_residence"]).reset_index(
        drop=True
    )

    return df


# Initialize Data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# ---------------------------------------------------------
# SIDEBAR FILTERS & CONTROLS
# ---------------------------------------------------------
st.sidebar.header("🎛️ Dashboard Controls")


def reset_filters():
    st.session_state["selected_states"] = list(df["state_of_residence"].unique())
    st.session_state["selected_months"] = MONTH_ORDER.copy()
    st.session_state["selected_sexes"] = list(df["sex_of_infant"].unique())


if "selected_states" not in st.session_state:
    st.session_state["selected_states"] = list(df["state_of_residence"].unique())
if "selected_months" not in st.session_state:
    st.session_state["selected_months"] = MONTH_ORDER.copy()
if "selected_sexes" not in st.session_state:
    st.session_state["selected_sexes"] = list(df["sex_of_infant"].unique())

st.sidebar.button("🔄 Reset All Filters", on_click=reset_filters)
st.sidebar.markdown("---")

# State Selection
all_states = sorted(df["state_of_residence"].unique())
select_all_states = st.sidebar.checkbox(
    "Select All States / Geographies", value=True
)

if select_all_states:
    default_states = all_states
else:
    default_states = st.session_state["selected_states"]

selected_states = st.sidebar.multiselect(
    "Select State(s) / Geography",
    options=all_states,
    default=default_states,
    key="selected_states",
)

# Month Selection
selected_months = st.sidebar.multiselect(
    "Select Month(s)",
    options=MONTH_ORDER,
    default=st.session_state["selected_months"],
    key="selected_months",
)

# Infant Sex Selection
selected_sexes = st.sidebar.multiselect(
    "Infant Sex",
    options=list(df["sex_of_infant"].unique()),
    default=st.session_state["selected_sexes"],
    key="selected_sexes",
)

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Filter Summary")
st.sidebar.text(f"Geographies: {len(selected_states)}/{len(all_states)}")
st.sidebar.text(f"Months: {len(selected_months)}/12")
st.sidebar.text(f"Sex Categories: {len(selected_sexes)}")

# Apply Filters
filtered_df = df[
    df["state_of_residence"].isin(selected_states)
    & df["month"].isin(selected_months)
    & df["sex_of_infant"].isin(selected_sexes)
]

# ---------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------
st.title("US Provisional Natality Explorer (2025)")
st.markdown(
    """
    Explore provisional monthly birth counts across US states and territories for analytic evaluation. 
    Designed for undergraduate business analytics coursework to examine seasonal trends, demographic breakdowns, and geographic variations.
    """
)

# Source & Governance Disclaimers
col_gov1, col_gov2 = st.columns(2)
with col_gov1:
    st.info(
        "🏛️ **Source Attribution:** Centers for Disease Control and Prevention (CDC) / National Center for Health Statistics (NCHS)."
    )
with col_gov2:
    st.warning(
        "⚠️ **Notice:** Data shown are **provisional** and represent absolute **birth counts**, not population-adjusted birth rates."
    )

st.markdown("---")

# Empty Filter Fallback
if filtered_df.empty:
    st.warning(
        "⚠️ No observations match the current filter criteria. Please adjust your sidebar selections."
    )
    st.stop()

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
total_births = filtered_df["births"].sum()
num_geos = filtered_df["state_of_residence"].nunique()
avg_monthly_births = (
    filtered_df.groupby("month")["births"].sum().mean()
    if not filtered_df.empty
    else 0
)

# Peak Geography Calculation
geo_grouped = filtered_df.groupby("state_of_residence")["births"].sum()
top_geo = geo_grouped.idxmax() if not geo_grouped.empty else "N/A"
top_geo_val = geo_grouped.max() if not geo_grouped.empty else 0

# Peak Month Calculation
month_grouped = filtered_df.groupby("month", observed=False)["births"].sum()
top_month = month_grouped.idxmax() if not month_grouped.empty else "N/A"
top_month_val = month_grouped.max() if not month_grouped.empty else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Births", f"{total_births:,.0f}")
kpi2.metric("Selected Geographies", f"{num_geos:,}")
kpi3.metric("Avg Births / Month", f"{avg_monthly_births:,.0f}")
kpi4.metric("Peak State", f"{top_geo}", f"{top_geo_val:,.0f} births")
kpi5.metric("Peak Month", f"{top_month}", f"{top_month_val:,.0f} births")

st.markdown("---")

# ---------------------------------------------------------
# DASHBOARD TABS
# ---------------------------------------------------------
tab_overview, tab_geo, tab_monthly, tab_table, tab_about = st.tabs(
    [
        "Overview",
        "Geographic Analysis",
        "Monthly & Sex Analysis",
        "Data Table & Download",
        "About the Data",
    ]
)

# --- TAB 1: OVERVIEW ---
with tab_overview:
    st.subheader("High-Level Distribution & Trends")

    col_ov1, col_ov2 = st.columns(2)

    with col_ov1:
        monthly_trend = (
            filtered_df.groupby(["month", "sex_of_infant"], observed=False)[
                "births"
            ]
            .sum()
            .reset_index()
        )
        fig_trend = px.line(
            monthly_trend,
            x="month",
            y="births",
            color="sex_of_infant",
            markers=True,
            title="Monthly Birth Trends by Infant Sex",
            labels={
                "month": "Month",
                "births": "Total Births",
                "sex_of_infant": "Infant Sex",
            },
        )
        fig_trend.update_layout(yaxis=dict(rangemode="tozero"))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_ov2:
        sex_dist = (
            filtered_df.groupby("sex_of_infant")["births"].sum().reset_index()
        )
        fig_sex = px.bar(
            sex_dist,
            x="sex_of_infant",
            y="births",
            color="sex_of_infant",
            title="Total Birth Count Comparison by Sex",
            labels={"sex_of_infant": "Infant Sex", "births": "Total Births"},
        )
        fig_sex.update_layout(yaxis=dict(rangemode="tozero"), showlegend=False)
        st.plotly_chart(fig_sex, use_container_width=True)

    st.markdown("### Quick Analytic Insights")
    st.markdown(
        f"- Under current filters, **{top_geo}** recorded the highest volume with **{top_geo_val:,.0f}** total births."
    )
    st.markdown(
        f"- Peak seasonal delivery occurred in **{top_month}** with **{top_month_val:,.0f}** recorded births across selected regions."
    )

# --- TAB 2: GEOGRAPHIC ANALYSIS ---
with tab_geo:
    st.subheader("Geographic Distribution & State Rankings")

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        state_totals = (
            filtered_df.groupby(
                ["state_of_residence", "state_abbr"], observed=False
            )["births"]
            .sum()
            .reset_index()
        )
        fig_map = px.choropleth(
            state_totals,
            locations="state_abbr",
            locationmode="USA-states",
            color="births",
            scope="usa",
            hover_name="state_of_residence",
            title="US State Choropleth Map (Birth Counts)",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_g2:
        state_ranked = state_totals.sort_values(by="births", ascending=True)
        top_bottom_df = state_ranked.tail(15)
        fig_bar = px.bar(
            top_bottom_df,
            x="births",
            y="state_of_residence",
            orientation="h",
            title="Top Selected States by Birth Count",
            labels={"births": "Total Births", "state_of_residence": "State"},
        )
        fig_bar.update_layout(xaxis=dict(rangemode="tozero"))
        st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: MONTHLY & SEX ANALYSIS ---
with tab_monthly:
    st.subheader("Seasonal Patterns & Demographic Breakdowns")

    heatmap_data = filtered_df.pivot_table(
        index="state_of_residence",
        columns="month",
        values="births",
        aggfunc="sum",
        observed=False,
    ).fillna(0)

    fig_heat = px.imshow(
        heatmap_data,
        labels=dict(x="Month", y="State", color="Birth Count"),
        title="State-by-Month Birth Heatmap",
        aspect="auto",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        monthly_agg = (
            filtered_df.groupby("month", observed=False)["births"]
            .sum()
            .reset_index()
        )
        fig_mo = px.bar(
            monthly_agg,
            x="month",
            y="births",
            title="Aggregated Birth Counts by Month",
            labels={"month": "Month", "births": "Birth Count"},
        )
        fig_mo.update_layout(yaxis=dict(rangemode="tozero"))
        st.plotly_chart(fig_mo, use_container_width=True)

    with col_m2:
        sex_month = (
            filtered_df.groupby(["month", "sex_of_infant"], observed=False)[
                "births"
            ]
            .sum()
            .reset_index()
        )
        fig_sm = px.bar(
            sex_month,
            x="month",
            y="births",
            color="sex_of_infant",
            barmode="group",
            title="Monthly Birth Counts Grouped by Infant Sex",
            labels={
                "month": "Month",
                "births": "Births",
                "sex_of_infant": "Sex",
            },
        )
        fig_sm.update_layout(yaxis=dict(rangemode="tozero"))
        st.plotly_chart(fig_sm, use_container_width=True)

# --- TAB 4: DATA TABLE & DOWNLOAD ---
with tab_table:
    st.subheader("Searchable Filtered Dataset")
    st.markdown(
        "Inspect and export the underlying raw data corresponding to your active filter parameters."
    )

    search_query = st.text_input("🔍 Search State or Month:", "")
    display_df = filtered_df.copy()

    if search_query:
        display_df = display_df[
            display_df["state_of_residence"].str.contains(
                search_query, case=False, na=False
            )
            | display_df["month"].str.contains(
                search_query, case=False, na=False
            )
        ]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="provisional_natality_filtered_2025.csv",
        mime="text/csv",
    )

# --- TAB 5: ABOUT THE DATA ---
with tab_about:
    st.subheader("Pedagogical Notes & Data Governance")
    st.markdown(
        """
        ### About the Dataset
        This dashboard utilizes provisional natality records from the **Centers for Disease Control and Prevention (CDC)** 
        National Center for Health Statistics (NCHS) for the year **2025**.
        
        ### Key Analytical Distinctions for Students:
        1. **Provisional Status:** Provisional data are based on records received and processed by NCHS as of a specified date. They may differ from final annual counts due to late reporting, corrections, or quality validation procedures.
        2. **Counts vs. Rates:** Figures represent absolute **birth counts**. In business analytics and demographic studies, comparing raw counts across states with vastly different population sizes (e.g., California vs. Wyoming) can be misleading. Consider normalizing data or evaluating per-capita metrics where appropriate.
        3. **Seasonality:** Monthly distributions often reveal seasonal patterns influenced by behavioral, meteorological, and recording cycles.
        
        ### Technical Stack
        - Built with **Python**, **Streamlit**, and **Plotly** for responsive, interactive visualization.
        """
    )
