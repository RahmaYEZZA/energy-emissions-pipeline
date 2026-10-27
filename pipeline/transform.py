"""Transform: keep countries only, join both sources and compute indicators."""
from pathlib import Path
import logging

import pandas as pd

from pipeline.config import COLUMNS, KEY, MIN_YEAR, STAGING_DIR

log = logging.getLogger(__name__)


def keep_countries(df: pd.DataFrame) -> pd.DataFrame:
    """OWID files mix countries with aggregates (World, continents...). Aggregates have
    no ISO code or an 'OWID_' code."""
    mask = df["iso_code"].notna() & ~df["iso_code"].astype(str).str.startswith("OWID")
    return df[mask]


def build_tables(co2: pd.DataFrame, energy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    co2 = keep_countries(co2[COLUMNS["co2"]])
    energy = keep_countries(energy[COLUMNS["energy"]])
    co2 = co2[co2["year"] >= MIN_YEAR]
    energy = energy[energy["year"] >= MIN_YEAR]

    fact = co2.merge(energy, on=KEY, how="left")
    # kg of CO2 per kWh of primary energy (co2 in Mt, energy in TWh)
    fact["carbon_intensity_kg_per_kwh"] = (
        fact["co2"] / fact["primary_energy_consumption"]).where(fact["primary_energy_consumption"] > 0)
    fact = fact.sort_values(KEY).reset_index(drop=True)
    fact["co2_change_pct"] = fact.groupby("iso_code")["co2"].pct_change(fill_method=None) * 100

    dim_country = (fact.sort_values("year").groupby("iso_code", as_index=False)
                   .agg(country=("country", "last"),
                        first_year=("year", "min"), last_year=("year", "max")))
    fact = fact.drop(columns=["country"])
    return dim_country, fact


def transform(paths: dict[str, str], run_date: str) -> dict[str, str]:
    co2 = pd.read_csv(paths["co2"])
    energy = pd.read_csv(paths["energy"])
    dim_country, fact = build_tables(co2, energy)

    out = STAGING_DIR / run_date
    out.mkdir(parents=True, exist_ok=True)
    files = {"dim_country": out / "dim_country.parquet",
             "fact_country_year": out / "fact_country_year.parquet"}
    dim_country.to_parquet(files["dim_country"], index=False)
    fact.to_parquet(files["fact_country_year"], index=False)
    log.info("dim_country: %d rows, fact_country_year: %d rows", len(dim_country), len(fact))
    return {k: str(v) for k, v in files.items()}
