# SQL Assignment — November 2025 Green Taxi Analysis

This assignment uses the NYC Green Taxi Trip dataset, which contains detailed records of taxi rides, including pickup and drop-off times, locations, distances, and fares recorded by the NYC Taxi & Limousine Commission (TLC).

The goal is to practice writing SQL queries to answer business and analytics questions about trips in **November 2025**.

---

## Question 3  
**For the trips in November 2025, how many trips had a `trip_distance` of less than or equal to 1 mile?**

```sql
SELECT COUNT(*) AS short_trip_count
FROM green_taxi_trips
WHERE DATE(lpep_pickup_datetime) BETWEEN '2025-11-01' AND '2025-11-30'
  AND trip_distance <= 1;
```
---
## Question 4

**Which was the pickup day with the longest trip distance? Only consider trips with trip_distance `less than 100 miles`.**

``` sql
SELECT 
    DATE(lpep_pickup_datetime) AS pickup_day,
    trip_distance
FROM green_taxi_trips
WHERE trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 1;
```
## Question 5
**Which was the pickup zone with the largest total amount (sum of all trips) on `November 18th, 2025`?**

``` sql
SELECT 
    z."Zone" AS pickup_zone,
    SUM(t.total_amount) AS total_revenue
FROM green_taxi_trips t
JOIN zones z
    ON t."PULocationID" = z."LocationID"
WHERE DATE(t.lpep_pickup_datetime) = '2025-11-18'
GROUP BY z."Zone"
ORDER BY total_revenue DESC
LIMIT 1;

```
## Question 6
**For the passengers picked up in the zone named `East Harlem North` in November 2025, which was the drop-off zone that had the largest tip?**

``` sql
SELECT 
    dz."Zone" AS dropoff_zone,
    MAX(t.tip_amount) AS largest_tip
FROM green_taxi_trips t
JOIN zones pz
    ON t."PULocationID" = pz."LocationID"
JOIN zones dz
    ON t."DOLocationID" = dz."LocationID"
WHERE pz."Zone" = 'East Harlem North'
  AND DATE(t.lpep_pickup_datetime) BETWEEN '2025-11-01' AND '2025-11-30'
GROUP BY dz."Zone"
ORDER BY largest_tip DESC
LIMIT 1;
End of SQL Assignment