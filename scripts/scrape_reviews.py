"""
scripts/scrape_reviews.py
==========================
**Standalone scraping script** — fetches Google Play reviews for the three
Ethiopian fintech bank apps and writes a raw (un-cleaned) CSV.

This script is intentionally separate from the cleaning and analysis steps so
each phase of the pipeline can be run, debugged, and scheduled independently.

Pipeline role
-------------
  scrape_reviews.py  →  clean_reviews.py  →  analyze_reviews.py

Usage
-----
    # From the project root (venv activated):
    python scripts/scrape_reviews.py

    # Override review count or output location:
    python scripts/scrape_reviews.py --count 400 --output data/raw_reviews.csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root is importable regardless of working directory
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.scraper import scrape_to_dataframe  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_OUTPUT = PROJECT_ROOT / "notebooks" / "data" / "raw_reviews.csv"


def run(count: int = 500, output: Path = DEFAULT_OUTPUT,
        lang: str = "en", country: str = "et") -> None:
    """Scrape reviews for all configured banks and save raw CSV."""
    logger.info("Starting scraping phase — %d reviews per bank.", count)
    df_raw = scrape_to_dataframe(count=count, lang=lang, country=country)

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    df_raw.to_csv(output, index=False)
    logger.info("Raw reviews saved → %s  (%d rows)", output, len(df_raw))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Scrape Google Play reviews for Ethiopian bank apps."
    )
    p.add_argument("--count", type=int, default=500,
                   help="Reviews per bank (default: 500).")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                   help=f"Output CSV path (default: {DEFAULT_OUTPUT}).")
    p.add_argument("--lang", default="en", help="Language code (default: en).")
    p.add_argument("--country", default="et", help="Country code (default: et).")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(count=args.count, output=args.output, lang=args.lang, country=args.country)
