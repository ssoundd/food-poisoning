from sitotoxism_data_loader import fetch_sitotoxism_data
import pandas as pd
from datetime import datetime

def get_summary_card():

    region_rows = fetch_sitotoxism_data("I2848")
    facility_rows = fetch_sitotoxism_data("I2849")
    virus_rows = fetch_sitotoxism_data("I2850")

    region_df = pd.DataFrame(region_rows)
    facility_df = pd.DataFrame(facility_rows)
    virus_df = pd.DataFrame(virus_rows)

    available_years = sorted(region_df["OCCRNC_YEAR"].dropna().unique())[-3:]
    recent_years = [str(y) for y in available_years]

    region_df = region_df[region_df['OCCRNC_YEAR'].isin(recent_years)]
    facility_df = facility_df[facility_df['OCCRNC_YEAR'].isin(recent_years)]
    virus_df = virus_df[virus_df['OCCRNC_YEAR'].isin(recent_years)]

    region_df["OCCRNC_MM"] = pd.to_numeric(region_df["OCCRNC_MM"], errors = "coerce")
    region_df["OCCRNC_CNT"] = pd.to_numeric(region_df["OCCRNC_CNT"], errors = "coerce")
    region_df["PATNT_CNT"] = pd.to_numeric(region_df["PATNT_CNT"], errors = "coerce")

    virus_df["PATNT_CNT"] = pd.to_numeric(virus_df["PATNT_CNT"], errors = "coerce")
    facility_df["PATNT_CNT"] = pd.to_numeric(facility_df["PATNT_CNT"], errors = "coerce")

    current_month = datetime.now().month
    current_month_data = region_df[region_df["OCCRNC_MM"] == current_month]

    avg_cnt = int(round(current_month_data["OCCRNC_CNT"].mean()))
    avg_patients = int(round(current_month_data["PATNT_CNT"].mean()))

    top_virus = (
        virus_df.groupby("OCCRNC_VIRS")["PATNT_CNT"]
        .sum()
        .reset_index()
        .sort_values("PATNT_CNT", ascending = False)
        .iloc[0]
    )

    top_facility = (
        facility_df.groupby("OCCRNC_PLC")["PATNT_CNT"]
        .sum()
        .reset_index()
        .sort_values("PATNT_CNT", ascending = False)
        .iloc[0]
    )

    return {
        "current_month" : current_month,
        "avg_cnt" : avg_cnt,
        "avg_patients" : avg_patients,
        "top_virus_name" : top_virus["OCCRNC_VIRS"],
        "top_virus_count" : int(top_virus["PATNT_CNT"]),
        "top_facility_name" : top_facility["OCCRNC_PLC"],
        "top_facility_count" : int(top_facility["PATNT_CNT"])
    }