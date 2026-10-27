"""Validate: stop the pipeline before bad data reaches the warehouse."""
import logging

import pandas as pd

from pipeline.config import COLUMNS

log = logging.getLogger(__name__)


class DataQualityError(Exception):
    pass


def check(df: pd.DataFrame, source: str) -> list[str]:
    """Return a list of problems (empty list = data is fine)."""
    problems = []
    missing = set(COLUMNS[source]) - set(df.columns)
    if missing:
        problems.append(f"{source}: missing columns {sorted(missing)}")
        return problems
    if len(df) < 1000:
        problems.append(f"{source}: only {len(df)} rows, the file looks truncated")
    if df["year"].max() < 2020:
        problems.append(f"{source}: latest year is {df['year'].max()}, data looks outdated")

    countries = df[df["iso_code"].notna() & ~df["iso_code"].astype(str).str.startswith("OWID")]
    dup = countries.duplicated(subset=["iso_code", "year"]).sum()
    if dup:
        problems.append(f"{source}: {dup} duplicated (iso_code, year) rows")

    for col in [c for c in COLUMNS[source] if c.endswith("_share_energy")]:
        bad = countries[col].dropna()
        bad = bad[(bad < 0) | (bad > 100.5)]
        if len(bad):
            problems.append(f"{source}: {len(bad)} values of {col} outside 0-100")
    for col in ["co2", "population", "primary_energy_consumption"]:
        if col in countries and (countries[col].dropna() < 0).any():
            problems.append(f"{source}: negative values in {col}")
    return problems


def validate(paths: dict[str, str]) -> dict[str, str]:
    all_problems = []
    for source, path in paths.items():
        df = pd.read_csv(path)
        problems = check(df, source)
        all_problems += problems
        log.info("%s: %d rows, %d problem(s)", source, len(df), len(problems))
    if all_problems:
        raise DataQualityError("\n".join(all_problems))
    return paths
