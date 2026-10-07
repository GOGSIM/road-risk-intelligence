# Road Risk Intelligence

Road Risk Intelligence is a research-to-production machine learning project for
estimating and ranking relative road-accident risk across spatial units and time
windows.

The project is currently an open-data Toronto pilot. It is not a deployed safety
system and it does not predict individual crashes with certainty. The intended
output is a relative-risk signal that can support human road-safety review.

## Current Status

**Current milestone: Week 2 event-level KSI cleaning and validation completed.**

The repository now contains:

- a `src`-layout Python package named `road_risk`;
- a reproducible data lifecycle under `data/`;
- exploratory feasibility analysis for Toronto collision data;
- event-level cleaning logic for the Toronto KSI dataset;
- SQL validation of the cleaned event-level table;
- one reusable source module, `road_risk.data.events`.

No machine learning model has been trained yet. No model metrics are reported at
this stage.

| Component | Status |
| --- | --- |
| Repository architecture | Implemented |
| Python package bootstrap | Implemented |
| Data lifecycle directories | Implemented |
| Week 1 data feasibility study | Completed |
| Toronto Traffic Collisions inspection | Completed |
| Toronto KSI inspection | Completed |
| Strict signalized-intersection feasibility decision | GO |
| Event-level KSI table construction | Implemented |
| Event-level data dictionary | Documented in notebook |
| SQL validation of event-level table | Completed |
| Reusable event-table builder in `src` | Implemented |
| Canonical spatial unit definition | Not finalized |
| Time-bucket definition | Not finalized |
| Negative-observation generation | Not started |
| Feature engineering | Not started |
| Model training and evaluation | Not started |
| API, database, deployment, monitoring | Deferred |

## Project Scope

The intended prediction unit is:

```text
road spatial unit x time window
```

The intended modeling task is:

```text
rare-event binary classification + relative-risk ranking
```

The final spatial unit, time bucket, prediction horizon, negative-observation
construction, and validation scheme are still open design decisions. The current
work establishes whether the source data can support that later dataset.

## Academic Foundation

The project is inspired by the research direction explored at Nagoya University:

**Towa Kitagawa.**
*Prediction and Information Provision of Traffic Accident Risk on Nagoya
Expressway.*
Master's thesis, Nagoya University, 2024.

The retained idea is that accident risk varies across both space and time and
should be treated as a contextual risk-estimation problem rather than as a
static accident map.

Reference:

https://www.trans.civil.nagoya-u.ac.jp/english/09.html

## Data Sources

The current pilot uses Toronto open data snapshots stored locally under
`data/raw/`. Raw snapshots are excluded from Git.

### Toronto Traffic Collisions Open Data

- Source: Toronto Police Service Public Safety Data Portal
- Dataset identifier: ASR-T-TBL-001
- Local snapshot date: 2026-10-05
- Observed rows: 825,265
- Observed unique collision events: 825,265
- Observed coverage: 2014-01-01 to 2026-06-30
- Role in project: broader collision context

This dataset is not treated as the authoritative source for killed-or-seriously
injured outcomes because the inspected schema does not provide the KSI target
definition needed by the pilot.

### Motor Vehicle Collisions with Killed or Seriously Injured Data

- Source: City of Toronto Open Data
- Local snapshot date: 2026-10-05
- Observed person-level rows: 20,771
- Observed unique collision events: 7,620
- Observed coverage: 2006-01-01 to 2026-09-15
- Coordinate system: WGS84 latitude and longitude
- Role in project: authoritative serious-collision outcome source

The KSI dataset is person-level. Multiple rows can represent people involved in
the same collision, so `collision_id` is the canonical event identifier.

## Main Findings So Far

### Week 1: Feasibility

The Toronto pilot is feasible with the inspected open data.

Key findings:

- the general Traffic Collisions dataset contains 825,265 unique collision
  events and is useful as context;
- the KSI dataset contains 20,771 person-level records representing 7,620 unique
  collision events;
- 7,619 of 7,620 KSI collision events have complete latitude and longitude;
- event-level values for inspected road-context fields such as `traffictl` and
  `accloc` are internally consistent within each `collision_id`;
- a strict pilot definition using `Traffic Signal` plus explicit intersection
  location categories yields 2,252 unique KSI collision events.

Decision:

```text
GO
```

The category `Intersection-Related` remains excluded from the strict pilot
definition until its interpretation is justified more clearly.

### Week 2: Event-Level KSI Cleaning

The raw person-level KSI dataset has been transformed into an event-level table:

```text
one row = one collision event
primary key = collision_id
```

The intermediate output is:

```text
data/interim/ksi_events.csv
```

This file is generated locally and excluded from Git. It should be recreated
from raw data and project code rather than committed.

Validated event-level results:

- 7,620 collision-level events;
- 7,620 unique `collision_id` values;
- no duplicate event rows;
- no missing `accdate` values after datetime conversion;
- spatial coordinates available for 7,619 of 7,620 events;
- selected event-level columns contain no conflicting non-missing values within
  a collision;
- missingness is documented without arbitrary imputation.

SQL validation independently confirmed the main event-table invariants.

## Notebooks

The current analysis notebooks are:

| Notebook | Purpose |
| --- | --- |
| `notebooks/01_data_feasibility.ipynb` | Inspect source datasets and decide whether the Toronto pilot is feasible |
| `notebooks/02_event_level_cleaning.ipynb` | Transform person-level KSI records into one row per collision event |
| `notebooks/03_sql_validation.ipynb` | Validate the cleaned event-level table with SQL checks |

Notebooks are investigative artifacts. Canonical reusable logic should move into
`src/road_risk/` when it becomes part of the project pipeline.

## Source Code

The implemented reusable code currently lives in:

```text
src/road_risk/data/events.py
```

It exposes:

```python
from road_risk.data.events import build_event_table
```

`build_event_table(df)`:

- requires `collision_id` and the configured event-level columns;
- checks for missing required columns;
- checks that selected event-level values do not conflict within a
  `collision_id`;
- drops person-level duplicates into one row per collision event;
- converts `accdate` to datetime;
- rejects missing collision IDs;
- verifies that the output has exactly one row per `collision_id`.

This is an intermediate cleaning utility, not a full ingestion or feature
engineering pipeline.

## Repository Structure

```text
road-risk-intelligence/
|-- .gitignore
|-- README.md
|-- pyproject.toml
|
|-- data/
|   |-- README.md
|   |-- raw/
|   |-- interim/
|   `-- processed/
|
|-- notebooks/
|   |-- 01_data_feasibility.ipynb
|   |-- 02_event_level_cleaning.ipynb
|   `-- 03_sql_validation.ipynb
|
`-- src/
    `-- road_risk/
        |-- __init__.py
        `-- data/
            |-- __init__.py
            `-- events.py
```

The repository uses a `src`-based Python package layout. The importable package
name is:

```python
road_risk
```

## Data Lifecycle

The project uses three data stages:

| Directory | Meaning | Git policy |
| --- | --- | --- |
| `data/raw/` | Immutable source snapshots | Data files ignored |
| `data/interim/` | Reproducible intermediate artifacts | Data files ignored |
| `data/processed/` | Future model-ready datasets | Data files ignored |

Directory placeholders are tracked with `.gitkeep` files.

Rules:

- raw data must not be manually edited;
- non-raw data must be reproducible from upstream data and project code;
- generated datasets should not be committed;
- canonical transformations belong in source code once they stabilize.

More detail is documented in `data/README.md`.

## Development Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the package in editable mode:

```powershell
python -m pip install -e .
```

Install analysis dependencies as needed:

```powershell
python -m pip install pandas jupyter
```

The project metadata currently declares the package and Python version, but it
does not yet pin the full notebook or analysis dependency set.

Verify the editable package import:

```powershell
python -c "import road_risk; print(road_risk.__file__)"
```

The path should resolve under:

```text
src/road_risk/
```

## Reproducing the Current Data Work

Expected local raw files:

```text
data/raw/Traffic_Collisions_Open_Data_8128730402587031536.csv
data/raw/Motor Vehicle Collisions with KSI Data - 4326.csv
```

Current workflow:

1. Run `notebooks/01_data_feasibility.ipynb` to inspect source data and confirm
   the pilot feasibility assumptions.
2. Run `notebooks/02_event_level_cleaning.ipynb` to produce
   `data/interim/ksi_events.csv`.
3. Run `notebooks/03_sql_validation.ipynb` to validate the event-level table
   with SQL checks.

The resulting `data/interim/ksi_events.csv` is an intermediate dataset. It is
not yet the final machine-learning observation table.

## Dataset Construction Contract

The source datasets contain recorded positive collision events. They do not
directly provide the final binary classification table.

The project still needs to construct an observation grid:

```text
spatial unit x time window
```

Then events can be assigned to observations:

```text
qualifying collision in spatial-time window -> target = 1
no qualifying collision in spatial-time window -> target = 0
```

Negative observations must:

- correspond to valid exposure opportunities;
- use the same spatial and temporal unit as positive observations;
- be constructed deterministically;
- avoid arbitrary sampling rules that redefine the task;
- be reproducible from documented code.

## Leakage and Validation Policy

Preventing leakage is a core project requirement.

Historical features must use only information available strictly before the
prediction timestamp. Weather, traffic, and other time-varying predictors must
represent information that would have been available at inference time.

Random row-level train/test splitting is not sufficient for final evaluation.
The intended validation direction is:

- chronological final test separation;
- temporal cross-validation or blocked validation within the training period;
- grouped or geographic checks where appropriate.

The final test period must remain untouched during feature selection, model
selection, hyperparameter tuning, threshold selection, and calibration decisions.

## Planned Evaluation

Because serious collisions are rare events, raw accuracy will not be a primary
metric.

Planned metrics include:

- PR-AUC;
- recall at top-K risk;
- Brier score;
- calibration analysis;
- precision and recall at selected operating points;
- slice-based error analysis.

No metric values should be reported until the dataset, target construction,
validation strategy, and holdout procedure are implemented.

## Roadmap

### Completed

- repository bootstrap;
- data lifecycle structure;
- Toronto source-data feasibility analysis;
- strict signalized-intersection pilot feasibility decision;
- event-level KSI cleaning;
- SQL validation of the event-level KSI table;
- reusable `build_event_table()` implementation.

### Next

- define the canonical spatial unit;
- define the time-bucket granularity;
- formalize event-to-observation assignment;
- construct deterministic negative observations;
- calculate target prevalence;
- move stable dataset-construction logic into `src/road_risk/data/`.

### Later

- leakage-safe feature engineering;
- historical-frequency baseline;
- logistic regression baseline;
- tree-based model experiments;
- temporal validation;
- probability calibration;
- error analysis;
- final untouched test evaluation;
- deployment-oriented API, database, CI, Docker, and monitoring only after the
  ML pipeline is validated.

## Responsible Use and Limitations

Road-accident risk estimation is safety-sensitive and highly imbalanced.

Important limitations:

- model outputs should support human review, not automated safety-critical
  action;
- low absolute predicted probability does not imply that a location is safe;
- high relative risk does not imply certainty that a collision will occur;
- historical collision patterns may reflect traffic exposure, reporting
  processes, infrastructure, and policy changes;
- results from Toronto do not automatically transfer to another city;
- the Traffic Collisions and KSI datasets serve different analytical purposes
  and must not be treated as equivalent target sources.

The modeling objective does not require personally identifiable information
about collision participants. Unnecessary personal information should not be
introduced into datasets, logs, databases, or public artifacts.

## Project Quality Rules

1. Do not report unreproduced model results.
2. Do not use the final test set for iterative modeling decisions.
3. Do not calculate historical features using future information.
4. Do not manually edit raw source data.
5. Do not keep canonical pipeline logic only inside notebooks.
6. Do not duplicate preprocessing logic across notebooks and source modules.
7. Do not generate negative observations with arbitrary exposure assumptions.
8. Do not introduce infrastructure before there is a concrete project need.
9. Do not describe planned components as implemented.
10. Keep public project documentation in English.

## References

Towa Kitagawa.
*Prediction and Information Provision of Traffic Accident Risk on Nagoya
Expressway.*
Nagoya University, 2024.

Nagoya University transportation research thesis list:

https://www.trans.civil.nagoya-u.ac.jp/english/09.html

Current pilot data sources:

- Toronto Police Service Public Safety Data Portal, Traffic Collisions Open Data,
  ASR-T-TBL-001
- City of Toronto Open Data, Motor Vehicle Collisions with Killed or Seriously
  Injured Data

Source attribution and Open Government Licence requirements must be preserved
when source data are used or redistributed.
