/* @bruin

# Docs:
# - Materialization: https://getbruin.com/docs/bruin/assets/materialization
# - Quality checks (built-ins): https://getbruin.com/docs/bruin/quality/available_checks
# - Custom checks: https://getbruin.com/docs/bruin/quality/custom

# TODO: Set the asset name (recommended: staging.trips).
name: staging.trips
type: duckdb.sql
depends:
  - ingestion.trips
  - ingestion.payment_lookup
materialization:
  type: table
custom_checks:
  - name: ZeroCheck
    description: Check that the number of rows in the staging.trips table is zero (i.e., no rows are present)
    query: |
      -- TODO: return a single scalar (COUNT(*), etc.) that should match `value`
      SELECT COUNT(*) FROM staging.trips
    value: 1
    count: 1

@bruin */
SELECT 
  t.tpep_pickup_datetime,
  t.vendor_id,
  t.pu_location_id,
  t.do_location_id,
  t.tpep_dropoff_datetime,
  t.passenger_count,
  t.trip_distance,
  t.ratecode_id,
  t.store_and_fwd_flag,
  pl.payment_type_name,
  COALESCE(t.fare_amount, 0)                AS fare_amount,
  COALESCE(t.extra, 0)                      AS extra,
  COALESCE(t.mta_tax, 0)                    AS mta_tax,
  COALESCE(t.tip_amount, 0)                 AS tip_amount,
  COALESCE(t.tolls_amount, 0)               AS tolls_amount,
  COALESCE(t.improvement_surcharge, 0)      AS improvement_surcharge,
  COALESCE(t.congestion_surcharge, 0)       AS congestion_surcharge,
  COALESCE(t.airport_fee, 0)                AS airport_fee,
  COALESCE(t.total_amount, 0)               AS total_amount,
  t.taxi_type,
  t.extracted_at
FROM ingestion.trips t
LEFT JOIN ingestion.payment_lookup pl 
  ON t.payment_type = pl.payment_type_id
WHERE 
  t.tpep_pickup_datetime >= '{{ start_datetime }}'
  AND t.tpep_pickup_datetime <  '{{ end_datetime }}'
  AND t.vendor_id IS NOT NULL 
  AND t.pu_location_id IS NOT NULL 
  AND t.do_location_id IS NOT NULL
  AND t.pu_location_id != t.do_location_id
  AND t.passenger_count BETWEEN 1 AND 6
  AND t.trip_distance > 0 
  AND t.total_amount > 0
  AND t.tpep_dropoff_datetime > t.tpep_pickup_datetime
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY 
    t.tpep_pickup_datetime, 
    t.vendor_id, 
    t.pu_location_id, 
    t.do_location_id 
  ORDER BY t.extracted_at DESC
) = 1;



