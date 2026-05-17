"""
scripts/clean_reviews.py
=========================
**Standalone cleaning script** — reads a raw reviews CSV (produced by
``scrape_reviews.py``) and applies the full preprocessing pipeline:

    1. Drop rows with NaN review text or rating
    2. Deduplicate by review_id (primary key)
    3. Normalise dates  →  'YYYY-MM-DD'
    4. Collapse whitespace in review text; drop empty reviews
    5. Validate ratings are in range [1, 5]

This script is intentionally separate from the scraping and analysis steps so
each phase can be run, debugged, and scheduled independently.

Pipeline role
-------------
  scrape_reviews.py  →  clean_reviews.py  →  analyze_reviews.py

Usage
-----
    # From the project root (venv activated):
    python scripts/clean_reviews.py

    # Specify custom input / output paths:
    python scripts/clean_reviews.py \\
        --input  notebooks/data/raw_reviews.csv \\
        --output notebooks/data/processed_reviews.csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Ensure project root is importable regardless of working directory
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.preprocessor import preprocess  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_INPUT  = PROJECT_ROOT / "notebooks" / "data" / "raw_reviews.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "notebooks" / "data" / "processed_reviews.csv"


def run(input_path: Path = DEFAULT_INPUT,
        output_path: Path = DEFAULT_OUTPUT) -> None:
    """Load raw CSV → preprocess → save cleaned CSV."""
    input_path = Path(input_path)
    if not input_path.exists():
        logger.error(
            "Input file not found: %s\n"
            "Run  python scripts/scrape_reviews.py  first.",
            input_path,
        )
        sys.exit(1)

    logger.info("Loading raw reviews from %s …", input_path)
    df_raw = pd.read_csv(input_path)
    logger.info("  → %d rows loaded.", len(df_raw))

    logger.info("Starting cleaning phase …")
    df_clean = preprocess(df_raw)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(output_path, index=False)
    logger.info("Cleaned reviews saved → %s  (%d rows)", output_path, len(df_clean))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Clean and preprocess raw Google Play reviews."
    )
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                   help=f"Raw reviews CSV (default: {DEFAULT_INPUT}).")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                   help=f"Output cleaned CSV (default: {DEFAULT_OUTPUT}).")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(input_path=args.input, output_path=args.output)
