import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden
import time

# -----------------------------
# CONFIGURATION
# -----------------------------

BUCKET_NAME = "dtc-de-2026-amrith-bucket"

GOOGLE_APPLICATION_CREDENTIALS = "/home/codespace/.gcp/keys/gcp_dtc-de-course.json"
client = storage.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)

# Base URLs for GitHub releases (yellow + green)
BASE_URLS = {
    "yellow": "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_",
    "green":  "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_"
}

YEARS = ["2019", "2020"]
MONTHS = [f"{i:02d}" for i in range(1, 13)]

DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bucket = client.bucket(BUCKET_NAME)

# -----------------------------
# DOWNLOAD FUNCTION
# -----------------------------

def download_file(args):
    taxi_type, year, month = args
    base_url = BASE_URLS[taxi_type]

    url = f"{base_url}{year}-{month}.csv.gz"
    file_path = os.path.join(DOWNLOAD_DIR, f"{taxi_type}_tripdata_{year}-{month}.csv.gz")

    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

# -----------------------------
# BUCKET CHECK / CREATE
# -----------------------------

def create_bucket(bucket_name):
    try:
        bucket = client.get_bucket(bucket_name)

        project_bucket_ids = [bckt.id for bckt in client.list_buckets()]
        if bucket_name in project_bucket_ids:
            print(f"Bucket '{bucket_name}' exists and belongs to your project.")
        else:
            print(f"Bucket '{bucket_name}' exists but not in your project.")
            sys.exit(1)

    except NotFound:
        bucket = client.create_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")

    except Forbidden:
        print(f"Bucket '{bucket_name}' exists but is not accessible. Choose another name.")
        sys.exit(1)

# -----------------------------
# VERIFY UPLOAD
# -----------------------------

def verify_gcs_upload(blob_name):
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)

# -----------------------------
# UPLOAD FUNCTION
# -----------------------------

def upload_to_gcs(file_path, max_retries=3):
    taxi_type = "yellow" if "yellow" in file_path else "green"
    blob_name = f"module4/{taxi_type}/{os.path.basename(file_path)}"

    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    create_bucket(BUCKET_NAME)

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME}/{blob_name} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            if verify_gcs_upload(blob_name):
                print(f"Verification successful for {blob_name}")
                return
            else:
                print(f"Verification failed for {blob_name}, retrying...")

        except Exception as e:
            print(f"Failed to upload {file_path}: {e}")

        time.sleep(5)

    print(f"Giving up on {file_path} after {max_retries} attempts.")

# -----------------------------
# MAIN EXECUTION
# -----------------------------

if __name__ == "__main__":
    create_bucket(BUCKET_NAME)

    # Create (taxi_type, year, month) tasks
    tasks = []
    for taxi_type in ["yellow", "green"]:
        for year in YEARS:
            for month in MONTHS:
                tasks.append((taxi_type, year, month))

    # Download files
    with ThreadPoolExecutor(max_workers=4) as executor:
        file_paths = list(executor.map(download_file, tasks))

    # Upload files
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(upload_to_gcs, filter(None, file_paths))

    print("All yellow + green files processed and verified.")
