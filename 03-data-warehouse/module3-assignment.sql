-- Create an external table using the Yellow Taxi Trip Records.

CREATE OR REPLACE EXTERNAL TABLE `dtc-de-course-2026-486806.yellow.external_yellow_2024`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dtc-de-2026-amrith-bucket/yellow_tripdata_2024-*.parquet']
);

---1 Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table).

CREATE OR REPLACE TABLE `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned` AS
SELECT *
FROM `dtc-de-course-2026-486806.yellow.external_yellow_2024`;


---2 Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.

SELECT COUNT(DISTINCT PULocationID)
FROM `dtc-de-course-2026-486806.yellow.external_yellow_2024`;


SELECT COUNT(DISTINCT PULocationID)
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`;


---3 Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table.

-- This query will process 155.12 MB when run.
SELECT PULocationID
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`;

-- This query will process 310.24 MB when run.
SELECT PULocationID, DOLocationID
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`;

---4 How many records have a fare_amount of 0?

SELECT count(*) as fare_amount
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`
WHERE fare_amount = 0;

---5 What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)

-- finding the number of vendors
SELECT COUNT(DISTINCT VendorID) AS distinct_vendor_ids
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`;


-- partioning and clustering table
CREATE OR REPLACE TABLE `dtc-de-course-2026-486806.yellow.yellow_2024_optimized`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT *
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`;


---6 Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive)

SELECT DISTINCT VendorID
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15';

SELECT DISTINCT VendorID
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_optimized`
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15';

---9 How many bytes does it estimate will be read? Why?
SELECT COUNT(*)
FROM `dtc-de-course-2026-486806.yellow.yellow_2024_non_partitioned`;


