"""@bruin

name: ingestion.trips
type: python
image: python:3.11

# connection to use for loading the table. DuckDB is our local default.
connection: duckdb-default

# Python materialization returns a DataFrame which Bruin writes to the destination.
# We append new rows each run and rely on later stages to dedupe.
materialization:
  type: table
  strategy: append

# Basic column definitions for lineage & quality checks.  Only a subset is declared
# here; DuckDB will infer the rest when we return the DataFrame at runtime.
columns:
  - name: taxi_type
    type: string
    description: "source taxi classification (yellow/green)"
  - name: extracted_at
    type: timestamp
    description: "UTC timestamp when the row was pulled from the source"

@bruin"""

import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd


# materialize will be called by Bruin when the asset runs. We read the
# date window from environment variables and the configured taxi_types
# from the pipeline variables (BRUIN_VARS).  Each month/taxi pair becomes a
# parquet URL that pandas can fetch directly.
def materialize():
    """Return a DataFrame containing raw taxi trips for the run window.

    Environment variables:
    - BRUIN_START_DATE, BRUIN_END_DATE: YYYY-MM-DD strings that define the
      inclusive window for this run.
    - BRUIN_VARS: JSON blob containing user-defined variables, notably
      ``taxi_types`` which is an array of strings (e.g. ["yellow"]).
    """

    # parse pipeline variables
    vars_json = os.environ.get("BRUIN_VARS", "{}")
    vars = json.loads(vars_json)
    taxi_types = vars.get("taxi_types", ["yellow"])

    # parse window
    start_str = os.environ.get("BRUIN_START_DATE")
    end_str = os.environ.get("BRUIN_END_DATE")
    if not start_str or not end_str:
        raise RuntimeError("BRUIN_START_DATE and BRUIN_END_DATE must be set")

    start_dt = datetime.fromisoformat(start_str)
    end_dt = datetime.fromisoformat(end_str)

    def month_iter(start: datetime, end: datetime):
        cur = start.replace(day=1)
        while cur <= end:
            yield cur
            cur = cur + relativedelta(months=1)

    frames: list[pd.DataFrame] = []

    for m in month_iter(start_dt, end_dt):
        year = m.year
        month = m.month
        for taxi in taxi_types:
            url = (
                f"https://d37ci6vzurychx.cloudfront.net/trip-data/"
                f"{taxi}_tripdata_{year}-{month:02d}.parquet"
            )
            # pandas will download & read via pyarrow
            df = pd.read_parquet(url)
            df["taxi_type"] = taxi
            df["extracted_at"] = datetime.utcnow()
            frames.append(df)

    if frames:
        return pd.concat(frames, ignore_index=True)
    else:
        # empty run produces empty frame with no columns
        return pd.DataFrame()


