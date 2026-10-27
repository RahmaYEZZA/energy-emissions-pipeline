-- Latest year available for each country, with its main indicators.
CREATE OR REPLACE TABLE mart_country_latest AS
WITH ranked AS (
    SELECT f.*,
           ROW_NUMBER() OVER (PARTITION BY f.iso_code ORDER BY f.year DESC) AS rn
    FROM fact_country_year AS f
    WHERE f.co2 IS NOT NULL
)
SELECT d.country,
       r.iso_code,
       r.year,
       r.co2,
       r.co2_per_capita,
       r.renewables_share_energy,
       r.low_carbon_share_energy,
       r.carbon_intensity_kg_per_kwh
FROM ranked AS r
JOIN dim_country AS d USING (iso_code)
WHERE r.rn = 1;
