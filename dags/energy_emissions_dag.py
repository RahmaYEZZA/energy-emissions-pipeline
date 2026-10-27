"""
Monthly pipeline: extract -> validate -> transform -> load.
Each task passes file paths (not data) to the next one through XCom.
"""
from datetime import datetime, timedelta

from airflow.sdk import dag, task

default_args = {"retries": 2, "retry_delay": timedelta(minutes=10)}


@dag(
    dag_id="energy_emissions_pipeline",
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["etl", "owid"],
)
def energy_emissions_pipeline():

    @task
    def extract_task(ds=None) -> dict:
        from pipeline.extract import extract
        return extract(ds)

    @task
    def validate_task(paths: dict) -> dict:
        from pipeline.validate import validate
        return validate(paths)  # raises DataQualityError and stops the run if checks fail

    @task
    def transform_task(paths: dict, ds=None) -> dict:
        from pipeline.transform import transform
        return transform(paths, ds)

    @task
    def load_task(files: dict) -> str:
        from pipeline.load import load
        return load(files)

    load_task(transform_task(validate_task(extract_task())))


energy_emissions_pipeline()
