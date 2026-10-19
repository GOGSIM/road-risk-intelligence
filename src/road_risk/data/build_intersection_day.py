import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT A — W04
# Reproducible intersection-day dataset preparation
# ============================================================

# 1. Paths and configuration

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRAFFIC_SIGNALS_PATH = (
    PROJECT_ROOT / "data/raw/traffic-signals.csv"
)

KSI_PATH = (
    PROJECT_ROOT / "data/interim/ksi_events.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data/processed"

START_DATE = pd.Timestamp("2018-01-01")
END_DATE = pd.Timestamp("2018-12-31")

# Preserve the cohort used in the W04 notebook.
SIGNAL_CUTOFF = pd.Timestamp("2018-09-01")


# ============================================================
# 2. Load datasets
# ============================================================

ts_df = pd.read_csv(TRAFFIC_SIGNALS_PATH)
ksi_events = pd.read_csv(KSI_PATH)

print("Traffic Signals:", ts_df.shape)
print("KSI events:", ksi_events.shape)


# ============================================================
# 3. Select signalized intersections
# ============================================================

ts_signals = ts_df[
    [
        "id",
        "mainStreet",
        "side1Street",
        "side2Street",
        "controlMode",
        "activationDate",
    ]
].copy()

signals_mask = (
    ~ts_signals["controlMode"].isin(
        ["PA - MPS", "PA - IPS"]
    )
    & ts_signals["controlMode"].notna()
)

ts_intersections = ts_signals.loc[
    signals_mask
].copy()

ts_intersections["activationDate"] = pd.to_datetime(
    ts_intersections["activationDate"]
)

signals = ts_intersections.loc[
    ts_intersections["activationDate"] <= SIGNAL_CUTOFF
].copy()

if not signals["id"].is_unique:
    raise ValueError("Traffic Signals IDs are not unique")

print("Selected intersections:", len(signals))


# ============================================================
# 4. Strict KSI filtering
# ============================================================

strict_accloc = [
    "At Intersection",
    "Four-way",
    "T Intersection",
    "Other Intersection",
    "Roundabout",
]

strict_mask = (
    (ksi_events["traffictl"] == "Traffic Signal")
    & ksi_events["accloc"].isin(strict_accloc)
)

strict_events = ksi_events.loc[strict_mask].copy()

events = strict_events.loc[
    strict_events["stname2"].notna()
].copy()

print("Strict KSI events:", len(strict_events))
print("Events with two streets:", len(events))


# ============================================================
# 5. Normalize street names
# ============================================================

for df, columns in [
    (
        signals,
        ["mainStreet", "side1Street", "side2Street"],
    ),
    (
        events,
        ["stname1", "stname2"],
    ),
]:
    for col in columns:
        normalized_col = col + "_normalized"

        df[normalized_col] = (
            df[col]
            .astype("string")
            .str.upper()
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.replace(r"\bAV\b", "AVE", regex=True)
            .str.replace(r"\bBV\b", "BLVD", regex=True)
        )


# ============================================================
# 6. Create canonical intersection keys
# ============================================================

events["intersection_key"] = events[
    ["stname1_normalized", "stname2_normalized"]
].apply(
    lambda row: " | ".join(sorted(row.tolist()))
    if row.notna().all() else pd.NA,
    axis=1,
)

signals["candidate_key_1"] = signals[
    ["mainStreet_normalized", "side1Street_normalized"]
].apply(
    lambda row: " | ".join(sorted(row.tolist()))
    if row.notna().all() else pd.NA,
    axis=1,
)

signals["candidate_key_2"] = signals[
    ["mainStreet_normalized", "side2Street_normalized"]
].apply(
    lambda row: " | ".join(sorted(row.tolist()))
    if row.notna().all() else pd.NA,
    axis=1,
)


# ============================================================
# 7. Build signal-key reference
# ============================================================

primary_keys = (
    signals[
        ["id", "activationDate", "candidate_key_1"]
    ]
    .rename(
        columns={"candidate_key_1": "intersection_key"}
    )
    .dropna(subset=["intersection_key"])
    .drop_duplicates(["id", "intersection_key"])
)

# Secondary street pairs are diagnostic only.
secondary_keys = (
    signals[
        ["id", "candidate_key_2"]
    ]
    .rename(
        columns={"candidate_key_2": "intersection_key"}
    )
    .dropna(subset=["intersection_key"])
    .drop_duplicates(["id", "intersection_key"])
)

key_id_counts = (
    primary_keys
    .groupby("intersection_key")["id"]
    .nunique()
)

unique_key_values = key_id_counts[
    key_id_counts == 1
].index

ambiguous_key_values = key_id_counts[
    key_id_counts > 1
].index

unique_signal_keys = (
    primary_keys.loc[
        primary_keys["intersection_key"].isin(
            unique_key_values
        )
    ]
    .drop_duplicates("intersection_key")
)


# ============================================================
# 8. Match KSI events to signal IDs
# ============================================================

events["event_date"] = pd.to_datetime(
    events["accdate"],
    errors="coerce",
).dt.normalize()

events = events.merge(
    unique_signal_keys,
    on="intersection_key",
    how="left",
    validate="many_to_one",
)

events["match_status"] = "matched"

events.loc[
    events["id"].isna(),
    "match_status",
] = "no_key_match"

events.loc[
    events["id"].isna()
    & events["intersection_key"].isin(
        secondary_keys["intersection_key"]
    ),
    "match_status",
] = "side2_unverified"

events.loc[
    events["id"].isna()
    & events["intersection_key"].isin(
        ambiguous_key_values
    ),
    "match_status",
] = "ambiguous_key"

events.loc[
    events["intersection_key"].isna(),
    "match_status",
] = "missing_street"

events.loc[
    events["event_date"].isna(),
    "match_status",
] = "invalid_date"

events.loc[
    events["id"].notna()
    & events["event_date"].notna()
    & (
        events["event_date"]
        < events["activationDate"]
    ),
    "match_status",
] = "inactive_at_event"


# ============================================================
# 9. Report unmatched events
# ============================================================

missing_street_events = strict_events.loc[
    strict_events["stname2"].isna(),
    ["collision_id", "accdate"],
].copy()

missing_street_events["intersection_key"] = pd.NA
missing_street_events["match_status"] = "missing_street"

unmatched_events = pd.concat(
    [
        events.loc[
            events["match_status"] != "matched",
            [
                "collision_id",
                "accdate",
                "intersection_key",
                "match_status",
            ],
        ],
        missing_street_events[
            [
                "collision_id",
                "accdate",
                "intersection_key",
                "match_status",
            ]
        ],
    ],
    ignore_index=True,
)

matching_report = (
    pd.concat(
        [
            events["match_status"],
            missing_street_events["match_status"],
        ],
        ignore_index=True,
    )
    .value_counts()
    .rename_axis("match_status")
    .reset_index(name="event_count")
)

matched_events = events.loc[
    events["match_status"] == "matched",
    ["id", "collision_id", "event_date"],
].copy()

matched_events = matched_events.rename(
    columns={"id": "intersection_id"}
)

matched_events["intersection_id"] = (
    matched_events["intersection_id"].astype("int64")
)

matched_events = matched_events.drop_duplicates(
    ["intersection_id", "collision_id", "event_date"]
)

print("\nKSI MATCHING REPORT")
print(matching_report.to_string(index=False))


# ============================================================
# 10. Build intersection x day grid
# ============================================================

prediction_dates = pd.DataFrame(
    {
        "prediction_date": pd.date_range(
            start=START_DATE,
            end=END_DATE,
            freq="D",
        )
    }
)

observation_grid = (
    signals[["id", "activationDate"]]
    .rename(columns={"id": "intersection_id"})
    .merge(prediction_dates, how="cross")
)

observation_grid = observation_grid.loc[
    observation_grid["activationDate"]
    <= observation_grid["prediction_date"]
].copy()

observation_grid["target_date"] = (
    observation_grid["prediction_date"]
    + pd.Timedelta(days=1)
)


# ============================================================
# 11. Aggregate KSI events by day
# ============================================================

daily_events = (
    matched_events
    .groupby(
        ["intersection_id", "event_date"]
    )["collision_id"]
    .nunique()
    .rename("daily_ksi")
    .reset_index()
)


# ============================================================
# 12. Create next-day target
# ============================================================

next_day_events = daily_events.rename(
    columns={
        "event_date": "target_date",
        "daily_ksi": "next_day_ksi",
    }
)

observation_grid = observation_grid.merge(
    next_day_events,
    on=["intersection_id", "target_date"],
    how="left",
    validate="one_to_one",
)

observation_grid["target"] = (
    observation_grid["next_day_ksi"]
    .fillna(0)
    .gt(0)
    .astype("int8")
)


# ============================================================
# 13. Historical KSI before prediction window
# ============================================================

history_before_window = (
    daily_events.loc[
        daily_events["event_date"] < START_DATE
    ]
    .groupby("intersection_id")["daily_ksi"]
    .sum()
    .rename("ksi_before_window")
)

observation_grid = observation_grid.merge(
    history_before_window,
    left_on="intersection_id",
    right_index=True,
    how="left",
    validate="many_to_one",
)


# ============================================================
# 14. Historical KSI within prediction window
# ============================================================

window_daily_events = (
    daily_events.loc[
        daily_events["event_date"].between(
            START_DATE,
            END_DATE,
        )
    ]
    .rename(
        columns={"event_date": "prediction_date"}
    )
)

observation_grid = observation_grid.merge(
    window_daily_events,
    on=["intersection_id", "prediction_date"],
    how="left",
    validate="one_to_one",
)

observation_grid["ksi_before_window"] = (
    observation_grid["ksi_before_window"]
    .fillna(0)
    .astype("int64")
)

observation_grid["daily_ksi"] = (
    observation_grid["daily_ksi"]
    .fillna(0)
    .astype("int64")
)

observation_grid = observation_grid.sort_values(
    ["intersection_id", "prediction_date"]
).reset_index(drop=True)

observation_grid["historical_ksi_count"] = (
    observation_grid["ksi_before_window"]
    + observation_grid.groupby("intersection_id")[
        "daily_ksi"
    ].cumsum()
    - observation_grid["daily_ksi"]
)


# ============================================================
# 15. Calendar feature
# ============================================================

observation_grid["day_of_week"] = (
    observation_grid["target_date"].dt.dayofweek
)


# ============================================================
# 16. Final dataset
# ============================================================

final_dataset = observation_grid[
    [
        "intersection_id",
        "prediction_date",
        "target_date",
        "day_of_week",
        "historical_ksi_count",
        "target",
    ]
].copy()


# ============================================================
# 17. Essential checks
# ============================================================

duplicate_count = final_dataset.duplicated(
    ["intersection_id", "prediction_date"]
).sum()

missing_count = final_dataset.isna().sum().sum()

if duplicate_count != 0:
    raise ValueError(
        f"Duplicate intersection-day rows: {duplicate_count}"
    )

if missing_count != 0:
    raise ValueError(
        f"Missing values detected: {missing_count}"
    )

if not final_dataset["target"].isin([0, 1]).all():
    raise ValueError("Invalid target values")

positive_count = int(final_dataset["target"].sum())
positive_share = final_dataset["target"].mean()

print("\nFINAL DATASET")
print("Shape:", final_dataset.shape)
print(
    "Unique intersections:",
    final_dataset["intersection_id"].nunique()
)
print("Positive observations:", positive_count)
print("Positive share:", f"{positive_share:.4%}")


# ============================================================
# 18. Save results
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

dataset_path = (
    OUTPUT_DIR / "intersection_day_2018.csv"
)

final_dataset.to_csv(
    dataset_path,
    index=False,
)

unmatched_events.to_csv(
    OUTPUT_DIR / "ksi_matching_exclusions.csv",
    index=False,
)

matching_report.to_csv(
    OUTPUT_DIR / "ksi_matching_report.csv",
    index=False,
)

print("\nDataset saved to:", dataset_path)
print("Pandas preparation completed.")
