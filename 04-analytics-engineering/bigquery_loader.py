from google.cloud import bigquery, storage
import os

# -----------------------------
# CONFIG
# -----------------------------

PROJECT_ID = "dtc-de-course-2026-486806"
DATASET_ID = "nytaxi"
BUCKET_NAME = "dtc-de-2026-amrith-bucket"

GOOGLE_APPLICATION_CREDENTIALS = "/home/codespace/.gcp/keys/gcp_dtc_bq_de.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

client_bq = bigquery.Client(project=PROJECT_ID)
client_gcs = storage.Client(project=PROJECT_ID)

TAXI_TYPES = ["yellow", "green"]

# -----------------------------
# LOAD FILES INTO BIGQUERY
# -----------------------------

def load_files(taxi_type):
    bucket = client_gcs.bucket(BUCKET_NAME)
    prefix = f"module4/{taxi_type}/"

    blobs = list(bucket.list_blobs(prefix=prefix))

    if not blobs:
        print(f"No files found for {taxi_type}.")
        return

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{taxi_type}_raw"

    job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=False,
    write_disposition="WRITE_APPEND",
    allow_jagged_rows=True
    )



    for blob in blobs:
        uri = f"gs://{BUCKET_NAME}/{blob.name}"
        print(f"Loading {uri} into {table_id}...")

        load_job = client_bq.load_table_from_uri(
            uri,
            table_id,
            job_config=job_config
        )

        load_job.result()
        print(f"Loaded {blob.name} into {table_id}")

# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    for taxi_type in TAXI_TYPES:
        load_files(taxi_type)

    print("All files loaded into BigQuery.")
