"""
scripts/run_pipeline.py
========================
CLI entry-point: scrape → preprocess → save CSV.

Usage
-----
    # From the project root (with your venv activated):
    python scripts/run_pipeline.py

    # Override review count and output path:
    python scripts/run_pipeline.py --count 400 --output data/reviews_clean.csv

    # Dry-run (skip live scraping; load an existing raw CSV instead):
    python scripts/run_pipeline.py --raw-input data/raw_reviews.csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so the script can be run from
# any working directory.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.scraper import scrape_to_dataframe       # noqa: E402
from scripts.preprocessor import preprocess           # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------
DEFAULT_OUTPUT = PROJECT_ROOT / "notebooks" / "data" / "processed_reviews.csv"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run(
    count: int = 500,
    output_path: Path = DEFAULT_OUTPUT,
    raw_input: Path | None = None,
    lang: str = "en",
    country: str = "et",
) -> pd.DataFrame:
    """
    Execute the full scrape → preprocess → save pipeline.

    Parameters
    ----------
    count       : Reviews to scrape per bank (ignored when *raw_input* given).
    output_path : Where to write the cleaned CSV.
    raw_input   : Optional path to a previously-scraped raw CSV; skips live
                  scraping so the pipeline can be re-run cheaply.
    lang        : Language code passed to the scraper.
    country     : Country code passed to the scraper.

    Returns
    -------
    The clean DataFrame that was saved to *output_path*.
    """
    # ------------------------------------------------------------------
    # Step 1 – Acquire raw data
    # ------------------------------------------------------------------
    if raw_input is not None:
        logger.info("Loading raw reviews from %s (skipping live scrape).", raw_input)
        df_raw = pd.read_csv(raw_input)
    else:
        logger.info("Scraping %d reviews per bank …", count)
        df_raw = scrape_to_dataframe(count=count, lang=lang, country=country)
        logger.info("Raw dataset shape: %s", df_raw.shape)

    # ------------------------------------------------------------------
    # Step 2 – Preprocess
    # ------------------------------------------------------------------
    df_clean = preprocess(df_raw)

    # ------------------------------------------------------------------
    # Step 3 – Save
    # ------------------------------------------------------------------
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(output_path, index=False)
    logger.info("Saved %d cleaned reviews → %s", len(df_clean), output_path)

    return df_clean


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape & preprocess Google Play reviews for Ethiopian banks."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=500,
        help="Number of reviews to scrape per bank (default: 500).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--raw-input",
        type=Path,
        default=None,
        metavar="CSV",
        help="Load raw reviews from this CSV instead of scraping live.",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Language code for the Play Store API (default: en).",
    )
    parser.add_argument(
        "--country",
        default="et",
        help="Country code for the Play Store API (default: et).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    run(
        count=args.count,
        output_path=args.output,
        raw_input=args.raw_input,
        lang=args.lang,
        country=args.country,
    )


if __name__ == "__main__":
    main()
