SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'ingestion.trips' 
  AND column_name LIKE '%location%'
  AND column_name LIKE '%PU%'
ORDER BY column_name;
