"""Central configuration: sources, paths and the columns we keep."""
from pathlib import Path
import os

ROOT = Path(os.getenv("PIPELINE_HOME", Path(__file__).resolve().parents[1]))
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
WAREHOUSE = Path(os.getenv("WAREHOUSE_PATH", DATA_DIR / "warehouse.duckdb"))
SQL_DIR = ROOT / "sql"

SOURCES = {
    "co2": "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv",
    "energy": "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv",
}

KEY = ["iso_code", "year"]

COLUMNS = {
    "co2": ["country", "iso_code", "year", "population", "co2", "co2_per_capita",
            "coal_co2", "oil_co2", "gas_co2"],
    "energy": ["iso_code", "year", "primary_energy_consumption", "energy_per_capita",
               "fossil_share_energy", "renewables_share_energy", "low_carbon_share_energy"],
}

MIN_YEAR = 1990
