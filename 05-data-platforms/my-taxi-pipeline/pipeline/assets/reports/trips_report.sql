/* @bruin

name: reports.trips_report
type: duckdb.sql
depends:
  - staging.trips

materialization:
  type: table
  
custom_checks:
  - name: row_count_positive
    description: Ensure daily aggregates have trips
    query: |
      SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END 
      FROM {{ this }}         
    value: 1                  # ← Now returns exactly 1 

@bruin */

WITH daily_data AS (
  SELECT 
    DATE(tpep_pickup_datetime) AS pickup_date,
    vendor_id,
    pu_location_id,
    COUNT(*) AS trip_count,
    SUM(total_amount) AS total_revenue,
    SUM(trip_distance) AS total_distance,
    SUM(fare_amount) AS total_fare,
    AVG(fare_amount) AS avg_fare,
    AVG(trip_distance) AS avg_distance,
    AVG(passenger_count) AS avg_passengers,
    COUNT(DISTINCT payment_type_name) AS unique_payment_types
  FROM staging.trips
  WHERE 
    tpep_pickup_datetime >= '{{ start_datetime }}'
    AND tpep_pickup_datetime < '{{ end_datetime }}'
  GROUP BY 1, 2, 3
)

SELECT * FROM daily_data
