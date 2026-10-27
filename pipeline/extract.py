"""Extract: download the raw files once per run date (re-running the same day is a no-op)."""
from datetime import date
from pathlib import Path
import logging
import urllib.request

from pipeline.config import RAW_DIR, SOURCES

log = logging.getLogger(__name__)


def extract(run_date: str | None = None) -> dict[str, str]:
    run_date = run_date or date.today().isoformat()
    target = RAW_DIR / run_date
    target.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, url in SOURCES.items():
        path = target / f"{name}.csv"
        if path.exists() and path.stat().st_size > 0:
            log.info("%s already downloaded, skipping", path)
        else:
            log.info("Downloading %s", url)
            tmp = path.with_suffix(".part")
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(path)  # atomic: no half-written file if the download fails
        paths[name] = str(path)
    return paths
