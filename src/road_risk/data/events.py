import pandas as pd

EVENT_COLUMNS = [
    "accdate",
    "stname1",
    "stname2",
    "stname3",
    "acclass",
    "accloc",
    "traffictl",
    "impactype",
    "visible",
    "light",
    "rdsfcond",
    "road_class",
    "longitude",
    "latitude",
    "division",
    "neighbourhood",
]

ID_COLUMN = "collision_id"

def build_event_table(df):
    
    required_columns = {ID_COLUMN, *EVENT_COLUMNS}
    missing_columns = required_columns - set(df.columns)
    
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )
        
    consistency = df.groupby(ID_COLUMN)[EVENT_COLUMNS].nunique(dropna=True)
    conflict_counts = (consistency > 1).sum() 
    conflicts = conflict_counts[conflict_counts > 0]
    
    if not conflicts.empty:
        raise ValueError(
            f"Conflicting event-level values: {conflicts.to_dict()}"
        )
    
    event_df = df[[ID_COLUMN] + EVENT_COLUMNS].drop_duplicates(subset=ID_COLUMN).copy()
    event_df.accdate = pd.to_datetime(event_df.accdate)
    missing_id_count = df[ID_COLUMN].isna().sum()

    if missing_id_count > 0:
        raise ValueError(
            f"{ID_COLUMN} contains {missing_id_count} missing values"
        )
        
    if len(event_df) != event_df[ID_COLUMN].nunique():
        raise ValueError(
            "Event table must contain exactly one row per collision_id"
        )

    return event_df