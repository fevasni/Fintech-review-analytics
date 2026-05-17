"""
scripts/analyze_reviews.py
===========================
**Standalone analysis script** — reads a cleaned reviews CSV (produced by
``clean_reviews.py``) and runs basic descriptive statistics + rating
distribution summaries.  Serves as the entry-point for the analysis phase
of the pipeline and can be extended with sentiment/thematic analysis.

Pipeline role
-------------
  scrape_reviews.py  →  clean_reviews.py  →  analyze_reviews.py

Usage
-----
    # From the project root (venv activated):
    python scripts/analyze_reviews.py

    # Point at a specific cleaned CSV:
    python scripts/analyze_reviews.py --input notebooks/data/processed_reviews.csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT   = Path(__file__).resolve().parent.parent
DEFAULT_INPUT  = PROJECT_ROOT / "notebooks" / "data" / "processed_reviews.csv"


def run(input_path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    """Load cleaned reviews and print a summary analysis report."""
    input_path = Path(input_path)
    if not input_path.exists():
        logger.error(
            "Cleaned reviews file not found: %s\n"
            "Run  python scripts/clean_reviews.py  first.",
            input_path,
        )
        sys.exit(1)

    logger.info("Loading cleaned reviews from %s …", input_path)
    df = pd.read_csv(input_path)
    logger.info("  → %d rows loaded.", len(df))

    # ------------------------------------------------------------------
    # Summary report
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("REVIEW DATASET SUMMARY")
    print("=" * 60)
    print(f"  Total reviews     : {len(df):,}")
    print(f"  Banks covered     : {df['bank'].nunique()}")
    print(f"  Date range        : {df['date'].min()}  →  {df['date'].max()}")
    print(f"  Columns           : {list(df.columns)}")

    print("\n--- Review count per bank ---")
    for bank, count in df["bank"].value_counts().items():
        print(f"  {bank:<20}: {count:>5,}")

    print("\n--- Rating distribution (all banks) ---")
    for rating in sorted(df["rating"].unique(), reverse=True):
        count = (df["rating"] == rating).sum()
        bar   = "█" * (count // 10)
        print(f"  {int(rating)} stars: {count:>5,}  {bar}")

    print("\n--- Average rating per bank ---")
    avg_ratings = df.groupby("bank")["rating"].mean().sort_values(ascending=False)
    for bank, avg in avg_ratings.items():
        print(f"  {bank:<20}: {avg:.2f}")

    print("=" * 60 + "\n")
    return df


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run descriptive analysis on cleaned fintech reviews."
    )
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                   help=f"Cleaned reviews CSV (default: {DEFAULT_INPUT}).")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(input_path=args.input)
