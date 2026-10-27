"""Load: replace the warehouse tables in one transaction, then rebuild the marts."""
import logging

import duckdb

from pipeline.config import SQL_DIR, WAREHOUSE

log = logging.getLogger(__name__)


def load(files: dict[str, str]) -> str:
    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE))
    try:
        con.execute("BEGIN")
        for table, path in files.items():
            con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet(?)", [path])
        for sql_file in sorted(SQL_DIR.glob("*.sql")):
            con.execute(sql_file.read_text())
            log.info("Built %s", sql_file.stem)
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    return str(WAREHOUSE)
