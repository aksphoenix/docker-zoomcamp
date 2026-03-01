"""@bruin
name: ingestion.trips
type: python
image: python:3.11

connection: duckdb-default

materialization:
  type: table
  strategy: append

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
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def month_iter(start: datetime, end: datetime):
    cur = start.replace(day=1)
    while cur <= end:
        yield cur
        cur = cur + relativedelta(months=1)


def materialize():
    """Return a DataFrame containing raw taxi trips for the run window.

    Environment variables:
    - BRUIN_START_DATE, BRUIN_END_DATE: YYYY-MM-DD strings (inclusive window).
    - BRUIN_VARS: JSON blob with user-defined variables, notably
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

    frames: list[pd.DataFrame] = []

    for taxi in taxi_types:
        for m in month_iter(start_dt, end_dt):
            year = m.year
            month = m.month
            url = (
                "https://d37ci6vzurychx.cloudfront.net/trip-data/"
                f"{taxi}_tripdata_{year}-{month:02d}.parquet"
            )
            logger.info("Fetching %s", url)
            try:
                df = pd.read_parquet(url)
            except Exception as exc:
                logger.warning("Skipping %s due to error: %s", url, exc)
                continue

            # add lineage columns
            df["taxi_type"] = taxi
            df["extracted_at"] = datetime.utcnow()

            frames.append(df)

    if not frames:
        logger.info("No frames built for window %s to %s", start_str, end_str)
        return pd.DataFrame()

    # concat once at the end to reduce overhead
    return pd.concat(frames, ignore_index=True)
