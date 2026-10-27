"""Run the whole pipeline locally, without Airflow:  python -m pipeline.run"""
from datetime import date
import argparse
import logging

from pipeline.extract import extract
from pipeline.validate import validate
from pipeline.transform import transform
from pipeline.load import load


def main(run_date: str | None = None) -> str:
    run_date = run_date or date.today().isoformat()
    raw = extract(run_date)
    validate(raw)
    staged = transform(raw, run_date)
    return load(staged)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-date", help="YYYY-MM-DD, defaults to today")
    print("Warehouse ready:", main(parser.parse_args().run_date))
