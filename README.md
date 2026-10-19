# Road Risk Intelligence

Road Risk Intelligence is a research-to-production machine learning project for
estimating and ranking relative road-accident risk across spatial units and time
windows.

The project is currently an open-data Toronto pilot. It is not a deployed safety
system and it does not predict individual crashes with certainty. The intended
output is a relative-risk signal that can support human road-safety review.

## Current Status

**Current milestone: Week 4 intersection-day dataset and exploratory baseline completed.**

The repository now contains:

- a `src`-layout Python package named `road_risk`;
- a reproducible data lifecycle under `data/`;
- exploratory feasibility analysis for Toronto collision data;
- event-level cleaning logic for the Toronto KSI dataset;
- SQL validation of the cleaned event-level table;
- a first in-notebook X/y prototype for signalized-intersection daily risk;
- a Traffic Signals inventory matched to KSI events;
- a reproducible 2018 intersection-day dataset builder in `src`;
- an in-notebook logistic-regression baseline with temporal validation.

The W4 model and its metrics are exploratory. There is no untouched final test
period, trained-model artifact, or deployed prediction service.

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
| Week 3 signalized-intersection-day prototype | Completed in notebook |
| Prototype observation grid | Implemented in notebook |
| Prototype target prevalence check | Completed |
| Week 4 Traffic Signals inventory and KSI matching | Implemented |
| 2018 intersection-day dataset and exclusion reports | Generated locally |
| Reusable dataset builder in `src` | Implemented as a script |
| Calendar and historical-count features | Implemented for W4 |
| Logistic-regression baseline and temporal checks | Completed in notebook |
| Final dataset and spatial definition | Still under validation |
| Untouched test evaluation | Not started |
| API, database, deployment, monitoring | Deferred |

## Project Scope

The long-term intended prediction unit is:

```text
road spatial unit x time window
```

The W3 and W4 pilots use a narrower unit:

```text
signalized intersection x prediction day
```

with a one-day prediction horizon.

The intended modeling task is:

```text
rare-event binary classification + relative-risk ranking
```

W4 uses Traffic Signals `id` as the intersection identifier and a daily
observation grid. This is a reproducible pilot definition, not a finalized
production dataset. The choice of spatial unit, broader time coverage, and
final validation scheme remain open.

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

### Toronto Traffic Signals

- Local input: `data/raw/traffic-signals.csv`
- Observed rows: 2,562
- Fields used: `id`, `mainStreet`, `side1Street`, `side2Street`,
  `controlMode`, and `activationDate`
- Role in project: intersection inventory for the W4 observation grid

W4 excludes pedestrian-activated modes `PA - MPS` and `PA - IPS`, as well as
missing `controlMode`. This leaves 2,432 records. Of these, 2,258 have an
`activationDate` on or before 2018-09-01 and form the W4 candidate cohort.
The cohort comes from the available snapshot; historical changes to control
mode and inventory completeness have not been independently verified.

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

### Week 3: Signalized-Intersection-Day Prototype

Week 3 builds the first learning-table prototype from the event-level KSI table.

Prototype task definition:

```text
prediction unit = one signalized intersection x one prediction day
prediction horizon = 1 day
target = 1 if a KSI collision is registered at the intersection on the next day
target = 0 otherwise
```

For this prototype, an intersection is represented by a canonical sorted pair of
`stname1` and `stname2`:

```text
street_a | street_b
```

GIS, OpenStreetMap, and Ontario Road Network geometries are not used yet. KSI
events with missing `stname2` are excluded because the intersection cannot be
identified reliably from the available street-name fields.

Key prototype results:

- 2,252 strict signalized-intersection KSI events from Week 1;
- 2,233 prototype events after excluding events without `stname2`;
- 1,430 unique prototype `intersection_key` values;
- 2,231 positive intersection-day observations;
- 1,103 candidate intersections known before 2018;
- September 2018 prototype window with 30 prediction days;
- 33,090 candidate intersection-day observations;
- 10 covered positive observations and 33,080 negative observations;
- prototype target prevalence of approximately 0.0302%.

The prototype includes early feature columns such as:

- `day_of_week`;
- `historical_ksi_count`, calculated using only events before the prediction
  date.

Important limitation of the W3 prototype: its candidate universe included only
intersections that appeared in KSI history before 2018. W4 introduces a
separate Traffic Signals inventory to address this selection bias, though its
historical completeness still needs validation.

### Week 4: Traffic Signals Dataset and Baseline

W4 replaces the KSI-derived candidate universe with a Traffic Signals inventory.
It normalizes street names (case, whitespace, `AV` to `AVE`, and `BV` to
`BLVD`) and matches strict signalized-intersection KSI events to a unique
`mainStreet` + `side1Street` pair. `side2Street` matches are recorded for
diagnostics only; ambiguous keys and events before a signal's activation date
are excluded from matched events.

Of 2,252 strict KSI events, 1,706 (75.75%) match a signal ID. The remaining
546 are documented in `ksi_matching_exclusions.csv`: 257 without a primary-key
match, 140 with an unverified `side2Street` match, 122 ambiguous keys, 19
missing second streets, and 8 events before activation.

The dataset builder creates one row per active candidate intersection and
prediction date from 2018-01-01 through 2018-12-31. The target is 1 when a
matched KSI event occurred at that intersection on `prediction_date + 1 day`.
It contains:

| Column | Meaning |
| --- | --- |
| `intersection_id` | Traffic Signals `id` |
| `prediction_date` | Day on which risk is estimated |
| `target_date` | Following day; date of the target outcome |
| `day_of_week` | Weekday of `target_date` (Monday = 0) |
| `historical_ksi_count` | Matched KSI events before `prediction_date` |
| `target` | Binary next-day matched KSI outcome |

Observed W4 output: 823,217 rows across 2,258 intersections, with 119
positive and 823,098 negative rows (positive share 0.0145%). Checks in the
notebook passed for unique intersection-day rows, required values, binary
targets, nonnegative history, target-date offset, and collision-to-intersection
uniqueness. Matching exclusions still limit outcome coverage: a zero means no
**matched** KSI event in that row's target window, not proof of no collision.

The notebook fits a `StandardScaler` + `LogisticRegression` baseline using
`day_of_week` and `historical_ksi_count`. Its chronological split uses
2018-01-01 through 2018-09-29 for training and 2018-10-01 through
2018-12-31 for validation, with 2018-09-30 left as a gap. Validation has
38 positive rows; the highest-scored 1% of rows contain 1 of them, for
Recall@1% of 2.63%. Three earlier temporal folds produce Recall@1% of
0.00%, 4.76%, and 7.14% (2 of 55 positives captured in total, pooled 3.64%).
These small positive counts and the incomplete match rate make the results
preliminary. No final holdout estimate or calibrated probabilities are claimed.

## Notebooks

The current analysis notebooks are:

| Notebook | Purpose |
| --- | --- |
| `notebooks/01_data_feasibility.ipynb` | Inspect source datasets and decide whether the Toronto pilot is feasible |
| `notebooks/02_event_level_cleaning.ipynb` | Transform person-level KSI records into one row per collision event |
| `notebooks/03_sql_validation.ipynb` | Validate the cleaned event-level table with SQL checks |
| `notebooks/04_signalized_intersection_day_prototype.ipynb` | Build the first signalized-intersection-day X/y prototype |
| `notebooks/05_traffic_signals_dataset.ipynb` | Inspect signal inventory, build W4 dataset, and evaluate an exploratory baseline |

Notebooks are investigative artifacts. W4 dataset preparation is also present
in a source script; the notebook and script should eventually share one
implementation to prevent their logic from drifting apart.

## Source Code

The implemented source code currently lives in:

```text
src/road_risk/data/events.py
src/road_risk/data/build_intersection_day.py
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

`build_intersection_day.py` is an executable Pandas script. It reads the local
Traffic Signals and interim KSI files, constructs the W4 grid and features,
checks basic invariants, and writes the dataset and matching reports. It runs
on import, so execute it as a script rather than importing it as a library
function. Model fitting and validation currently live in notebook 05.

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
|   |-- 03_sql_validation.ipynb
|   |-- 04_signalized_intersection_day_prototype.ipynb
|   `-- 05_traffic_signals_dataset.ipynb
|
`-- src/
    `-- road_risk/
        |-- __init__.py
        `-- data/
            |-- __init__.py
            |-- events.py
            `-- build_intersection_day.py
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
| `data/processed/` | Generated modeling datasets and diagnostic reports | Data files ignored |

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

Install the analysis and W4 baseline dependencies:

```powershell
python -m pip install pandas jupyter scikit-learn
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
data/raw/traffic-signals.csv
```

Current workflow:

1. Run `notebooks/01_data_feasibility.ipynb` to inspect source data and confirm
   the pilot feasibility assumptions.
2. Run `notebooks/02_event_level_cleaning.ipynb` to produce
   `data/interim/ksi_events.csv`.
3. Run `notebooks/03_sql_validation.ipynb` to validate the event-level table
   with SQL checks.
4. Run `notebooks/04_signalized_intersection_day_prototype.ipynb` to build the
   first signalized-intersection-day X/y prototype.
5. From the repository root, run the W4 dataset builder:

   ```powershell
   python src/road_risk/data/build_intersection_day.py
   ```

6. Open `notebooks/05_traffic_signals_dataset.ipynb` from `notebooks/` to
   inspect the matching diagnostics, rerun the dataset preparation, and run
   the baseline and temporal validation cells.

The resulting `data/interim/ksi_events.csv` is an intermediate dataset. It is
not yet the final machine-learning observation table.

The W4 script writes these ignored, local files:

```text
data/processed/intersection_day_2018.csv
data/processed/ksi_matching_exclusions.csv
data/processed/ksi_matching_report.csv
```

Notebook 05 also writes `intersection_day_2018_09.csv`. Despite its suffix,
the notebook's prediction window covers the full year 2018. The script output
`intersection_day_2018.csv` is the clearly named dataset to use for W4.

## Dataset Construction Contract

The source datasets contain recorded positive collision events. They do not
directly provide the final binary classification table.

W4 constructs an observation grid:

```text
spatial unit x time window
```

Matched events are then assigned to observations:

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

Week 3 implements the first prototype version of this contract for September
2018:

```text
candidate signalized intersections known before 2018
x
daily prediction dates from 2018-09-01 through 2018-09-30
```

W4 extends the grid to 2018 using Traffic Signals IDs and excludes days before
each signal's `activationDate`. Outcomes are limited to conservatively matched
KSI events. The W4 snapshot and matching coverage still need validation before
the resulting negatives can be treated as a final dataset contract.

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

W4 uses a chronological train/validation split and three earlier temporal
folds. It has no reserved final test period. A future test period must remain
untouched during feature selection, model selection, hyperparameter tuning,
threshold selection, and calibration decisions.

## Planned Evaluation

Because serious collisions are rare events, raw accuracy will not be a primary
metric.

The W4 notebook reports Recall@1% for its baseline. Further planned metrics
include:

- PR-AUC;
- recall at top-K risk;
- Brier score;
- calibration analysis;
- precision and recall at selected operating points;
- slice-based error analysis.

Current Recall@1% values describe only the W4 development sample; they are
not final generalization estimates.

## Roadmap

### Completed

- repository bootstrap;
- data lifecycle structure;
- Toronto source-data feasibility analysis;
- strict signalized-intersection pilot feasibility decision;
- event-level KSI cleaning;
- SQL validation of the event-level KSI table;
- reusable `build_event_table()` implementation;
- Week 3 signalized-intersection-day task definition;
- first in-notebook X/y prototype for September 2018;
- prototype leakage-safe historical count feature;
- W4 Traffic Signals cohort and conservative KSI-to-signal matching;
- reproducible 2018 intersection-day dataset and matching reports;
- in-notebook logistic-regression baseline and temporal validation.

### Next

- validate Traffic Signals inventory coverage and historical signal status;
- review excluded KSI matches, especially `side2Street` and ambiguous keys;
- decide whether the final spatial unit needs geometry-backed matching;
- expand leakage-safe features beyond weekday and historical KSI count;
- reserve a chronological final test period outside the W4 development sample;
- consolidate notebook and script dataset preparation;
- turn notebook baseline and validation into reproducible source code.

### Later

- richer leakage-safe feature engineering;
- historical-frequency baseline comparison;
- tree-based model experiments;
- broader temporal and geographic validation;
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
