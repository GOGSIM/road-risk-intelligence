# Road Accident Risk Intelligence

Road Accident Risk Intelligence is a machine learning decision-support project for estimating and ranking relative road-accident risk across spatial units and time windows.

The project is designed as a reproducible research-to-production ML system. Its intended use is to help road operators, municipal road-safety teams, and transportation analysts prioritize locations and time periods for further inspection, analysis, and safety review.

The system is not intended to predict individual crashes with certainty or to classify a location as absolutely safe or dangerous. Model outputs are treated as relative-risk estimates that support human decision-making.

---

## 1. Academic Foundation

The project is based on the research direction explored at Nagoya University in:

**Towa Kitagawa.**  
*Prediction and Information Provision of Traffic Accident Risk on Nagoya Expressway.*  
Master's thesis, Nagoya University, 2024.

The academic idea retained by this project is that traffic-accident risk varies across both space and time and should therefore be modeled as a contextual risk-estimation problem rather than as a static accident map.

Road Accident Risk Intelligence adapts this research direction to an open-data pilot in **Toronto, Canada**.

The project extends the original research idea toward a reproducible machine learning system with explicit dataset construction, leakage-safe validation, probability calibration, model versioning, and later deployment-oriented components.

Academic reference:

https://www.trans.civil.nagoya-u.ac.jp/english/09.html

---

## 2. Problem Definition

Road accidents are rare events whose probability is not distributed uniformly across a road network.

Risk may depend on factors such as:

- road and intersection characteristics;
- time of day and day of week;
- weather conditions;
- traffic exposure;
- recent accident history;
- local spatial context.

The project therefore treats road-safety risk as a spatiotemporal machine learning problem.

### Intended prediction unit

```text
road spatial unit × time window
```

The final spatial unit and time-bucket granularity have not yet been frozen.

Week 1 established that a signalized-intersection pilot is feasible, but the canonical observation unit will be finalized during dataset construction.

### Intended machine learning task

```text
rare-event binary classification + relative-risk ranking
```

The future model will estimate risk for each spatial-temporal observation and rank observations relative to one another.

The exact target horizon and observation granularity will be determined empirically from target prevalence and temporal sparsity.

---

## 3. Intended Use

The primary intended users are:

- road operators;
- municipal road-safety teams;
- transportation infrastructure analysts.

A future operational workflow is expected to be:

1. construct observations for a set of road locations and time windows;
2. estimate accident risk for each observation;
3. rank observations by relative risk;
4. inspect the highest-risk cases together with their context;
5. use the ranking as one input to a human safety-review process.

The project is a **decision-support system**, not an automated safety decision system.

### Out of scope

The project does not aim to provide:

- deterministic crash prediction;
- navigation or route guidance;
- autonomous driving;
- real-time driver warnings;
- road-safety certification;
- causal claims about accident causes;
- automatic safety-critical actions.

---

## 4. Current Project Status

**Current milestone: Week 1 completed — Toronto collision-data feasibility study.**

The repository bootstrap and the first empirical data investigation are complete.

No machine learning model has been trained yet.

| Component | Status |
|---|---|
| Repository architecture | Implemented |
| Python `src` layout | Implemented |
| Python package bootstrap | Implemented and verified |
| Virtual environment | Implemented |
| Editable package installation | Verified |
| Data lifecycle structure | Implemented |
| Data lifecycle rules | Defined |
| Week 1 data-source feasibility | Completed |
| Toronto Traffic Collisions inspection | Completed |
| Toronto KSI schema inspection | Completed |
| KSI event-level analysis | Completed |
| Coordinate feasibility analysis | Completed |
| Signalized-intersection pilot feasibility | Completed |
| Pilot feasibility decision | **GO** |
| Canonical ingestion pipeline in `src/` | Not started |
| Canonical spatial unit definition | Not finalized |
| Time-bucket definition | Not finalized |
| Negative-observation generation | Not started |
| Target prevalence analysis | Not started |
| Full exploratory data analysis | Not started |
| Feature engineering | Not started |
| Baseline models | Not started |
| Model evaluation | Not started |
| API / database / monitoring | Deferred |

No model-performance metrics are reported at this stage.

Metrics will only be published after the dataset, target construction, validation strategy, and final holdout procedure have been defined and implemented.

---

## 5. Week 1 — Data Feasibility Study

Week 1 focused on answering a prerequisite question before any modeling work:

> Is there enough open, structured, spatially usable collision data to support a credible Toronto pilot?

The analysis is documented in:

[`notebooks/01_data_feasibility.ipynb`](notebooks/01_data_feasibility.ipynb)

### 5.1 Data sources examined

#### Toronto Traffic Collisions

- **Source:** Toronto Police Service Public Safety Data Portal
- **Dataset:** Traffic Collisions Open Data
- **Dataset identifier:** ASR-T-TBL-001
- **Snapshot downloaded:** 2026-10-05
- **Format:** CSV
- **Observed coverage:** 2014-01-01 to 2026-06-30
- **Licence:** Open Government Licence

#### Motor Vehicle Collisions with Killed or Seriously Injured Data

- **Source:** City of Toronto Open Data
- **Dataset:** Motor Vehicle Collisions with Killed or Seriously Injured (KSI) Data
- **Snapshot downloaded:** 2026-10-05
- **Format:** CSV
- **Spatial reference:** WGS84 coordinates available
- **Observed coverage:** 2006-01-01 to 2026-09-15
- **Licence:** Open Government Licence

Raw source snapshots are stored locally under `data/raw/` and are excluded from Git.

---

## 6. Week 1 Findings

### General Traffic Collisions dataset

The inspected Toronto Traffic Collisions snapshot contains:

```text
825,265 rows
825,265 unique collision events
23 columns
```

The one-row-per-event structure makes the dataset useful for broader collision context.

However, the inspected schema does not provide a sufficiently precise distinction between serious injuries and other injury collisions for the intended KSI-oriented target definition.

For this reason, the general Traffic Collisions dataset is **not treated as the authoritative KSI outcome source**.

---

### KSI dataset

The inspected KSI snapshot contains:

```text
20,771 person-level rows
7,620 unique collision events
50 columns
```

The dataset is person-level rather than strictly collision-level.

This means that multiple rows can belong to the same collision event and must not be interpreted as independent collisions.

The canonical collision identifier is therefore essential when constructing event-level observations.

### Coordinate availability

Event-level coordinate coverage is nearly complete:

```text
7,619 / 7,620 unique KSI collision events
```

have complete latitude and longitude information in the inspected snapshot.

This confirms that the dataset is spatially usable for the Toronto pilot.

### Event-level consistency

Important road-context fields inspected during Week 1 were consistent within individual collision events.

In particular, the examined event-level values of:

```text
traffictl
accloc
```

did not produce contradictory values inside the same `collision_id`.

This supports aggregation from person-level rows to collision-level records.

---

## 7. Pilot Definition

Week 1 tested whether a strict intersection-focused pilot could provide enough positive events for further work.

The feasibility subset currently requires:

```text
Traffic Signal
+
explicit intersection-location category
```

The resulting strict subset contains:

```text
2,252 unique KSI collision events
```

This is large enough to justify continuing to Week 2.

### Important semantic decision

The category:

```text
Intersection-Related
```

is not currently included in the strict pilot definition.

Its semantic meaning is broader than an explicitly located intersection event and requires further justification before being merged into the canonical pilot population.

The project therefore prefers a narrower but better-defined pilot over an artificially larger sample with ambiguous semantics.

---

## 8. Week 1 Feasibility Decision

### Decision

```text
GO
```

The currently inspected Toronto open data are sufficient to continue building the pilot dataset.

The KSI dataset is the authoritative source for serious-collision outcomes in the current pilot.

The broader Traffic Collisions dataset remains useful as a contextual source, but it must not be treated as equivalent to the KSI dataset for serious-injury target definition.

This is a **data-feasibility decision**, not a finalized ML target definition.

The following decisions remain open:

- canonical spatial unit;
- time-bucket size;
- prediction horizon;
- negative-observation construction;
- traffic exposure representation;
- external road metadata;
- weather-data integration.

These will be addressed incrementally.

---

## 9. Current Repository Structure

```text
road-risk-intelligence/
├── .gitignore
├── README.md
├── pyproject.toml
│
├── data/
│   ├── README.md
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── notebooks/
│   └── 01_data_feasibility.ipynb
│
└── src/
    └── road_risk/
        ├── __init__.py
        └── data/
            └── __init__.py
```

The repository follows a `src`-based Python package layout.

The importable package is:

```python
road_risk
```

The `src/` directory is a repository-level source-code boundary and is not part of the public Python import path.

---

## 10. Data Lifecycle

The project defines three canonical data stages.

### `data/raw/`

Original source-data snapshots.

Properties:

- immutable;
- never manually edited;
- preserve the representation received from the original source;
- serve as the reproducibility starting point.

### `data/interim/`

Reproducible intermediate datasets generated from raw data.

Future examples may include:

- normalized collision timestamps;
- decoded categorical fields;
- event-level KSI records;
- cleaned coordinates;
- collision-to-spatial-unit mappings;
- intermediate temporal aggregations.

An interim dataset is not necessarily ready for machine learning.

### `data/processed/`

Canonical model-ready datasets generated by the project pipeline.

The intended processed representation will eventually contain observations similar to:

```text
spatial_unit_id
timestamp_bucket
road / intersection features
temporal features
historical features
target
```

Dataset files are excluded from normal Git tracking.

Repository structure, documentation, notebooks, metadata, and source code remain version controlled.

Further data-specific rules are documented in:

[`data/README.md`](data/README.md)

---

## 11. Architecture Principles

The following principles are permanent project rules.

### 11.1 Reproducibility over convenience

Every important result must be reproducible from:

```text
source data
+
versioned project code
+
documented configuration
```

Manual transformations that cannot be reproduced programmatically are not part of the canonical pipeline.

---

### 11.2 Raw data are immutable

Files stored under:

```text
data/raw/
```

must never be manually edited after ingestion.

Any correction, decoding, filtering, normalization, or transformation must be performed by project code and written to a downstream data stage.

---

### 11.3 Generated datasets must be reproducible

Every non-raw dataset must be reproducible from upstream data and project code.

The canonical data lineage is:

```text
raw
  ↓
interim
  ↓
processed
```

---

### 11.4 Notebooks are for investigation

The `notebooks/` directory is intended for:

- data feasibility analysis;
- exploratory data analysis;
- hypothesis testing;
- visualization;
- temporary investigation;
- error analysis.

Notebooks must not become the only implementation of canonical:

- preprocessing;
- dataset construction;
- feature engineering;
- model training;
- evaluation.

Once experimental logic becomes part of the canonical project pipeline, it must move into:

```text
src/road_risk/
```

The intended dependency direction is:

```text
notebooks
    ↓
src/road_risk
```

and never the reverse.

---

### 11.5 Canonical logic lives in `src`

Reusable project logic belongs under:

```text
src/road_risk/
```

The package grows only when a new responsibility is actually implemented.

Empty architectural layers are not created merely because they might become useful later.

---

### 11.6 Architecture grows with the project

New modules and infrastructure are introduced only when there is a concrete requirement for them.

Future areas such as:

```text
features/
modeling/
evaluation/
tests/
api/
db/
monitoring/
```

will be introduced only when the corresponding project stage begins.

---

### 11.7 Documentation must reflect reality

README files, metrics, architecture descriptions, experiment reports, and portfolio claims must describe the actual implemented state.

Future components must be explicitly marked as planned.

Unperformed experiments must never be described as completed work.

---

## 12. Dataset Construction Contract

The collision datasets contain recorded positive events.

They do not directly provide the final binary classification table required by the project.

The project must therefore construct a canonical observation grid:

```text
spatial unit × time window
```

Collision events will then be assigned to their corresponding observations.

Conceptually:

```text
qualifying collision in spatial-time window
        → target = 1

no qualifying collision in spatial-time window
        → target = 0
```

This dataset-construction step is a core ML-engineering problem rather than a minor preprocessing task.

### Negative observations

Negative examples must:

- correspond to valid exposure opportunities;
- be constructed deterministically;
- follow the same spatial and temporal unit as positive observations;
- avoid arbitrary sampling rules that redefine the task;
- be reproducible from documented code.

Week 1 established event-source feasibility.

Week 2 is responsible for turning the positive collision events into a reproducible pilot observation table.

---

## 13. Leakage Policy

Preventing data leakage is a primary methodological requirement.

### Historical information

Any feature representing historical information must use only information available strictly before the prediction timestamp.

For example:

```text
historical_accident_count_30d
```

for an observation at time `t` must not contain information from time `t` or any future timestamp.

---

### Future external information

Weather, traffic, and other time-varying features must reflect only information that would have been available at the intended prediction time.

Actual future observations must not be used as inference-time predictors unless the real application would have had access to them.

---

## 14. Validation Policy

Random row-level train/test splitting is not considered sufficient for final model evaluation.

The intended evaluation strategy is:

- chronological separation between training and final testing;
- temporal cross-validation or blocked temporal validation inside the training period;
- grouped or geographical evaluation where appropriate.

### Final test set

The final chronological test period must remain untouched during:

- feature selection;
- model selection;
- hyperparameter tuning;
- threshold selection;
- calibration-strategy selection.

It should be evaluated only after modeling decisions have been finalized.

---

## 15. Planned Evaluation Metrics

Road accidents and serious collisions are rare events.

For this reason, raw accuracy will not be used as the primary measure of model quality.

### Primary metric

```text
PR-AUC
```

### Secondary metrics

Planned secondary measures include:

- Recall at top-K risk;
- Brier score;
- probability calibration;
- precision and recall at selected operating points;
- slice-based error analysis.

Potential evaluation slices include:

- rain vs. dry conditions;
- day vs. night;
- intersection-context categories;
- common vs. rare spatial units;
- different road-context groups.

No metric values will be reported until they have been produced by the implemented validation pipeline.

---

## 16. Probability and Risk Interpretation

A rare event may have a low absolute predicted probability even when it is substantially riskier than other observations.

Future outputs are therefore expected to distinguish between:

```text
raw / calibrated probability
```

and:

```text
relative risk / ranking
```

A low numerical probability must not be interpreted as evidence that a location is safe.

A high relative-risk rank must not be interpreted as certainty that a collision will occur.

---

## 17. Reproducibility Policy

The project is intended to maintain traceability between:

```text
source data
→ processed data
→ features
→ experiment
→ model
→ evaluation
```

As the implementation grows, reproducibility metadata is expected to include:

- source-data snapshot;
- source download date;
- preprocessing version;
- feature schema;
- train/validation/test boundaries;
- random seeds where relevant;
- model configuration;
- evaluation results;
- Git commit identifier;
- model version.

A model result without enough information to reproduce the corresponding experiment is not considered a final project result.

---

## 18. Python Project Structure

### Repository name

```text
road-risk-intelligence
```

### Python distribution name

```text
road-risk-intelligence
```

### Python import name

```python
road_risk
```

The project uses:

- Python 3.11 as the current development environment;
- `setuptools` as the build backend;
- `pyproject.toml` for package metadata and build configuration;
- editable package installation during development.

---

## 19. Development Environment

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate on Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Activate on Linux or macOS

```bash
source .venv/bin/activate
```

### Install the project in editable mode

```bash
python -m pip install -e .
```

### Verify the package installation

```bash
python -c "import road_risk; print(road_risk.__file__)"
```

A correct editable installation should resolve the package to:

```text
src/road_risk/
```

The local `.venv/` directory is development-machine state and is not part of the repository.

---

## 20. Development Roadmap

The project is developed incrementally.

### Week 1 — Data feasibility

**Status: completed**

Completed work:

- inspected Toronto Traffic Collisions data;
- inspected Toronto KSI collision data;
- documented data coverage and licensing;
- distinguished row-level and event-level semantics;
- verified spatial-coordinate availability;
- checked event-level consistency of important road-context fields;
- tested a strict signalized-intersection pilot definition;
- selected the KSI dataset as the pilot serious-collision outcome source;
- recorded an explicit feasibility decision: **GO**.

---

### Week 2 — Pilot dataset construction

**Status: next milestone**

The next stage is expected to establish:

1. the canonical spatial unit;
2. the canonical event-level KSI table;
3. a defensible time-bucket granularity;
4. deterministic mapping from events to spatial-time observations;
5. valid negative observations;
6. target prevalence;
7. the first reusable ingestion and dataset-construction logic inside `src/road_risk/data/`.

No feature engineering or model training should begin before the observation unit, target construction, and leakage boundaries are explicit.

---

### Later modeling stages

Planned later work includes:

- exploratory data analysis;
- leakage-safe feature engineering;
- historical-frequency baseline;
- Logistic Regression baseline;
- additional tree-based model families;
- temporal validation;
- geographical or grouped validation;
- probability calibration;
- error analysis;
- final untouched test evaluation.

Production-oriented layers such as API serving, PostgreSQL integration, Docker, CI, and monitoring are intentionally deferred until the ML pipeline has been validated.

---

## 21. Responsible Use and Limitations

Road-accident risk estimation is a safety-sensitive and highly imbalanced modeling problem.

### Rare-event uncertainty

Even a well-performing model may assign relatively low absolute probabilities because serious collisions are rare.

### Exposure confounding

Historical collision counts may reflect traffic volume and exposure in addition to underlying road risk.

Traffic-related variables must therefore be interpreted carefully.

### Spatial bias

Different areas, road classes, infrastructure types, and reporting processes may follow different distributions.

Performance in Toronto does not automatically imply performance in another city or country.

### Temporal drift

Road infrastructure, traffic behavior, weather conditions, regulations, and reporting systems change over time.

Historical model performance does not guarantee future performance.

### Source-definition risk

The inspected Toronto collision datasets serve different analytical purposes.

The general Traffic Collisions dataset must not be treated as equivalent to the KSI dataset when defining a serious-collision outcome.

### Human-in-the-loop use

Predictions are intended to prioritize human review.

They must not directly trigger safety-critical actions without additional human and domain evaluation.

### Privacy

The modeling objective does not require personally identifiable information about collision participants.

Unnecessary personal information should not be introduced into:

- datasets;
- model inputs;
- databases;
- logs;
- public artifacts.

---

## 22. Project Quality Rules

The following rules apply throughout development.

1. Do not report model results that have not been reproduced.
2. Do not use the final test set for model or feature selection.
3. Do not calculate historical features using future information.
4. Do not manually modify raw source data.
5. Do not keep canonical pipeline logic only inside notebooks.
6. Do not duplicate preprocessing logic across notebooks and reusable source code.
7. Do not generate negative observations using arbitrary logic disconnected from valid exposure units.
8. Do not introduce infrastructure without a concrete project requirement.
9. Do not claim that the system predicts individual collisions with certainty.
10. Do not describe unfinished components as implemented.
11. Keep public project documentation in English.
12. Record material assumptions explicitly.
13. Record unresolved semantic questions explicitly.
14. Distinguish exploratory analysis from canonical pipeline logic.
15. Keep the final test set isolated from iterative modeling decisions.

---

## 23. References

### Academic foundation

Towa Kitagawa.  
*Prediction and Information Provision of Traffic Accident Risk on Nagoya Expressway.*  
Nagoya University, 2024.

Nagoya University transportation research thesis list:

https://www.trans.civil.nagoya-u.ac.jp/english/09.html

### Current pilot data sources

**Toronto Police Service Public Safety Data Portal**  
Traffic Collisions Open Data — ASR-T-TBL-001

**City of Toronto Open Data**  
Motor Vehicle Collisions with Killed or Seriously Injured (KSI) Data

The applicable source attribution and Open Government Licence requirements must be preserved when the data are used or redistributed.