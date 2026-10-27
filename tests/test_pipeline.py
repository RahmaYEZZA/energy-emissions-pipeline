import pandas as pd
import pytest

from pipeline.transform import build_tables, keep_countries
from pipeline.validate import check


def co2_df(**overrides):
    rows = [
        {"country": "Spain", "iso_code": "ESP", "year": 2023, "population": 48e6, "co2": 210.0,
         "co2_per_capita": 4.4, "coal_co2": 10.0, "oil_co2": 120.0, "gas_co2": 60.0},
        {"country": "Spain", "iso_code": "ESP", "year": 2024, "population": 48e6, "co2": 220.0,
         "co2_per_capita": 4.6, "coal_co2": 9.0, "oil_co2": 125.0, "gas_co2": 62.0},
        {"country": "World", "iso_code": "OWID_WRL", "year": 2024, "population": 8e9, "co2": 38000.0,
         "co2_per_capita": 4.7, "coal_co2": 1.0, "oil_co2": 1.0, "gas_co2": 1.0},
    ]
    df = pd.DataFrame(rows)
    for k, v in overrides.items():
        df[k] = v
    return df


def energy_df():
    return pd.DataFrame([
        {"iso_code": "ESP", "year": 2024, "primary_energy_consumption": 1600.0, "energy_per_capita": 33000.0,
         "fossil_share_energy": 66.0, "renewables_share_energy": 26.0, "low_carbon_share_energy": 34.0},
    ])


def test_aggregates_are_removed():
    assert set(keep_countries(co2_df())["iso_code"]) == {"ESP"}


def test_build_tables_joins_and_computes_indicators():
    dim, fact = build_tables(co2_df(), energy_df())
    assert list(dim["country"]) == ["Spain"]
    row_2024 = fact[fact["year"] == 2024].iloc[0]
    assert row_2024["carbon_intensity_kg_per_kwh"] == pytest.approx(220 / 1600)
    assert row_2024["co2_change_pct"] == pytest.approx((220 / 210 - 1) * 100)
    # 2023 has no energy data: the join must keep the row with empty energy columns
    assert fact[fact["year"] == 2023]["primary_energy_consumption"].isna().all()


def test_check_detects_missing_columns():
    problems = check(co2_df().drop(columns=["co2"]), "co2")
    assert any("missing columns" in p for p in problems)


def test_check_detects_duplicates_and_bad_shares():
    energy = pd.concat([energy_df()] * 2, ignore_index=True)
    energy.loc[0, "renewables_share_energy"] = 140
    problems = " ".join(check(energy, "energy"))
    assert "duplicated" in problems and "outside 0-100" in problems
