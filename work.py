
import pandas as pd
import numpy as np
from pathlib import Path

INPUT = Path("British Airways Summer Schedule Dataset - Forage Data Science Task 1.xlsx")
OUTPUT_XLSX = Path("BA_Lounge_Eligibility_Model.xlsx")
OUTPUT_LOOKUP = Path("BA_Lounge_Eligibility_Lookup.csv")
OUTPUT_SAMPLE = Path("BA_Lounge_Eligibility_Sample.csv")

# -----------------------------
# 1. Load and validate dataset
# -----------------------------
df = pd.read_excel(INPUT)

required = [
    "FLIGHT_DATE", "FLIGHT_TIME", "TIME_OF_DAY",
    "FLIGHT_NO", "ARRIVAL_REGION", "HAUL",
    "FIRST_CLASS_SEATS", "BUSINESS_CLASS_SEATS", "ECONOMY_SEATS",
    "TIER1_ELIGIBLE_PAX", "TIER2_ELIGIBLE_PAX", "TIER3_ELIGIBLE_PAX"
]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Scheduled capacity proxy. This is not booked passenger load.
seat_cols = ["FIRST_CLASS_SEATS", "BUSINESS_CLASS_SEATS", "ECONOMY_SEATS"]
df["TOTAL_SEATS"] = df[seat_cols].fillna(0).sum(axis=1)

# -----------------------------
# 2. Calculate observed rates
# -----------------------------
for tier in [1, 2, 3]:
    df[f"TIER{tier}_OBS_RATE"] = np.where(
        df["TOTAL_SEATS"] > 0,
        df[f"TIER{tier}_ELIGIBLE_PAX"] / df["TOTAL_SEATS"],
        0
    )

group_cols = ["HAUL", "ARRIVAL_REGION", "TIME_OF_DAY"]

lookup = (
    df.groupby(group_cols, dropna=False)
      .agg(
          flights=("FLIGHT_NO", "count"),
          avg_capacity=("TOTAL_SEATS", "mean"),
          tier1_observed_rate=("TIER1_OBS_RATE", "mean"),
          tier2_observed_rate=("TIER2_OBS_RATE", "mean"),
          tier3_observed_rate=("TIER3_OBS_RATE", "mean")
      )
      .reset_index()
)

# Round the dataset-derived averages into easy-to-apply assumptions.
# Rates are rounded to the nearest 0.1 percentage point.
for tier in [1, 2, 3]:
    lookup[f"TIER{tier}_ASSUMPTION"] = (
        lookup[f"tier{tier}_observed_rate"] * 100
    ).round(1)

# -----------------------------
# 3. Apply assumptions
# -----------------------------
model_lookup = lookup[
    group_cols + [
        "flights", "avg_capacity",
        "TIER1_ASSUMPTION", "TIER2_ASSUMPTION", "TIER3_ASSUMPTION"
    ]
].copy()

df_model = df.merge(
    model_lookup[group_cols + [
        "TIER1_ASSUMPTION", "TIER2_ASSUMPTION", "TIER3_ASSUMPTION"
    ]],
    on=group_cols,
    how="left"
)

for tier in [1, 2, 3]:
    df_model[f"EST_TIER{tier}_PAX"] = (
        df_model["TOTAL_SEATS"] *
        df_model[f"TIER{tier}_ASSUMPTION"] / 100
    ).round().astype(int)

# -----------------------------
# 4. Select a representative sample
# -----------------------------
# One flight from every non-empty category demonstrates that the
# lookup table is reusable across the schedule.
sample = (
    df_model.sort_values(["HAUL", "ARRIVAL_REGION", "TIME_OF_DAY", "FLIGHT_DATE", "FLIGHT_NO"])
            .groupby(group_cols, dropna=False, as_index=False)
            .head(1)
            .copy()
)
# -----------------------------
# 5. Save outputs
# -----------------------------

# Save the full model to Excel
with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
    df_model.to_excel(writer, sheet_name="Flight Model", index=False)
    model_lookup.to_excel(writer, sheet_name="Lookup Table", index=False)
    sample.to_excel(writer, sheet_name="Representative Sample", index=False)

# Save CSV versions
model_lookup.to_csv(OUTPUT_LOOKUP, index=False)
sample.to_csv(OUTPUT_SAMPLE, index=False)

print("\n" + "=" * 60)
print("FILES CREATED SUCCESSFULLY")
print("=" * 60)
print(f"Excel : {OUTPUT_XLSX.resolve()}")
print(f"Lookup: {OUTPUT_LOOKUP.resolve()}")
print(f"Sample: {OUTPUT_SAMPLE.resolve()}")
print("=" * 60)