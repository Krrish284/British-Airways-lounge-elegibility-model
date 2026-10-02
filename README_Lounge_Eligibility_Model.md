# British Airways Lounge Eligibility Model

## Purpose

This project builds a reusable, category-based model to estimate the percentage of passengers likely to be eligible for three lounge tiers:

- **Tier 1:** Concorde Room — treated as a hypothetical/potential future Tier 1 lounge at Terminal 3, not as a confirmed current facility.
- **Tier 2:** First Lounge
- **Tier 3:** Club Lounge

The model is designed for the British Airways Forage Data Science Task 1 and avoids assigning assumptions to individual flight numbers.

## Source data

Input file:

`British Airways Summer Schedule Dataset - Forage Data Science Task 1.xlsx`

The supplied schedule contains 10,000 flights covering 1 April 2025 through 30 October 2025.

Relevant fields include:

- `FLIGHT_DATE`
- `FLIGHT_TIME`
- `TIME_OF_DAY`
- `ARRIVAL_REGION`
- `HAUL`
- `FIRST_CLASS_SEATS`
- `BUSINESS_CLASS_SEATS`
- `ECONOMY_SEATS`
- `TIER1_ELIGIBLE_PAX`
- `TIER2_ELIGIBLE_PAX`
- `TIER3_ELIGIBLE_PAX`

## Modeling approach

### 1. Category definition

Each flight is grouped using:

`HAUL + ARRIVAL_REGION + TIME_OF_DAY`

This creates a reusable lookup structure rather than assumptions tied to specific flight numbers.

The dataset contains:

- Short-haul and long-haul flights
- Europe, North America, Middle East and Asia
- Morning, Lunchtime, Afternoon and Evening departures

### 2. Passenger/capacity measure

The model calculates:

`TOTAL_SEATS = FIRST_CLASS_SEATS + BUSINESS_CLASS_SEATS + ECONOMY_SEATS`

This is a **scheduled capacity proxy**, not actual booked passenger volume. Actual passenger counts would be preferable if load-factor data were available.

### 3. Eligibility rates

For each flight, the supplied tier eligibility counts are divided by total scheduled seats:

`Observed Tier Rate = Tier Eligible Pax / Total Seats`

The model then calculates the average observed rate for every:

`HAUL + ARRIVAL_REGION + TIME_OF_DAY`

category.

These category-level averages are rounded to the nearest **0.1 percentage point** and used as the model assumptions.

This approach makes the assumptions data-informed while keeping them simple enough to apply to future schedules.

### 4. Estimated lounge demand

For each flight:

`Estimated Tier Pax = Total Seats × Category Eligibility %`

The result is rounded to the nearest whole passenger.

## Why this structure?

The assignment asks for assumptions that are:

- Logical
- Justifiable
- Easy to apply to future schedules
- Independent of individual flight numbers

For example, an assumption such as:

`LONG + North America + Evening → Tier 2 = X%`

can be applied to any future flight matching those characteristics.

An assumption such as:

`Flight BA123 → Tier 2 = X%`

would not scale if the schedule or flight numbers changed.

## Representative sample

The script selects one flight from each non-empty category. This gives a compact sample covering the available combinations while demonstrating how the lookup table can be applied.

The full schedule does not need to be manually analyzed for the task because the category-level lookup table is designed to generalize across it.

## Outputs

Running the script produces:

### `BA_Lounge_Eligibility_Model.xlsx`

Contains:

- **Summary** — dataset and sample overview
- **Eligibility Lookup** — reusable category-level assumptions
- **Representative Sample** — sample flights with estimated Tier 1/2/3 eligible passengers

### `BA_Lounge_Eligibility_Lookup.csv`

Reusable lookup table containing the assumptions.

### `BA_Lounge_Eligibility_Sample.csv`

Representative sample showing the calculations.

## Important modeling limitation

The existing `TIER1_ELIGIBLE_PAX`, `TIER2_ELIGIBLE_PAX`, and `TIER3_ELIGIBLE_PAX` fields are part of the supplied educational dataset. Therefore, the resulting percentages should be treated as **model assumptions/baselines for this exercise**, not as official British Airways eligibility rules.

Tier 1 should also be interpreted as a **hypothetical potential lounge requirement**, as instructed by the task. The model does not imply that a Concorde Room currently exists at Terminal 3.

## How to run

Place these files in the same folder:

```text
British Airways Summer Schedule Dataset - Forage Data Science Task 1.xlsx
lounge_eligibility_model.py
```

Then run:

```bash
python lounge_eligibility_model.py
```

Required Python packages:

```bash
pip install pandas numpy openpyxl
```

The script will generate the three output files described above.
