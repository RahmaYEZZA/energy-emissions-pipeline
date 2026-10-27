-- Change in emissions and energy mix between 1990 and the latest year.
CREATE OR REPLACE TABLE mart_change_since_1990 AS
SELECT d.country,
       l.iso_code,
       b.co2                                             AS co2_1990,
       l.co2                                             AS co2_latest,
       ROUND(100 * (l.co2 / NULLIF(b.co2, 0) - 1), 1)    AS co2_change_pct,
       b.low_carbon_share_energy                         AS low_carbon_share_1990,
       l.low_carbon_share_energy                         AS low_carbon_share_latest
FROM mart_country_latest AS l
JOIN fact_country_year   AS b ON b.iso_code = l.iso_code AND b.year = 1990
JOIN dim_country         AS d ON d.iso_code = l.iso_code;
