"""
scripts/insert_reviews.py
==========================
Standalone script to load, merge, and insert cleaned reviews and bank data
into the PostgreSQL database.

Usage:
    python scripts/insert_reviews.py
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLEAN = PROJECT_ROOT / "notebooks" / "data" / "processed" / "cleaned_bank_reviews.csv"
DEFAULT_PROC = PROJECT_ROOT / "notebooks" / "processed_reviews.csv"

DB_CONFIG = {
    "host": "localhost",
    "database": "bank_review",
    "user": "admin",
    "password": "admin123"
}


def merge_and_prepare_data(clean_path: Path, proc_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load both CSVs, run order-preserving greedy matching, and prepare bank dataframe."""
    logger.info("Loading cleaned bank reviews from: %s", clean_path)
    df_clean = pd.read_csv(clean_path)

    if proc_path.exists():
        logger.info("Loading processed reviews with sentiment from: %s", proc_path)
        df_proc = pd.read_csv(proc_path)

        # Order-preserving greedy matching on review text
        clean_groups = {text: rows for text, rows in df_clean.groupby('review')}
        used_indices = set()
        merged_rows = []

        for _, proc_row in df_proc.iterrows():
            text = proc_row['review_text']
            if text in clean_groups:
                for _, clean_row in clean_groups[text].iterrows():
                    clean_idx = clean_row.name
                    if clean_idx not in used_indices:
                        used_indices.add(clean_idx)
                        merged_row = clean_row.to_dict()
                        merged_row.update(proc_row.to_dict())
                        merged_rows.append(merged_row)
                        break

        # Append any remaining clean reviews that weren't in df_proc
        for idx, clean_row in df_clean.iterrows():
            if idx not in used_indices:
                merged_row = clean_row.to_dict()
                merged_row['review_id'] = idx + 1
                merged_row['review_text'] = clean_row['review']
                merged_row['sentiment_label'] = 'Neutral'
                merged_row['identified_theme'] = 'General'
                merged_rows.append(merged_row)

        df_reviews = pd.DataFrame(merged_rows)
    else:
        logger.warning("Processed reviews file %s not found. Using defaults for sentiment/theme.", proc_path)
        df_reviews = df_clean.copy()
        df_reviews['review_id'] = df_reviews.index + 1
        df_reviews['review_text'] = df_reviews['review']
        df_reviews['sentiment_label'] = 'Neutral'
        df_reviews['identified_theme'] = 'General'

    # Re-assign review_id to be a clean, unique sequential sequence starting from 1
    df_reviews['review_id'] = range(1, len(df_reviews) + 1)

    # Add defaults if columns are missing
    df_reviews['sentiment_score'] = df_reviews.get('sentiment_score', 0.0)
    df_reviews['review_date'] = df_reviews.get('date', '2026-05-19')
    df_reviews['source'] = df_reviews.get('source', 'Google Play')

    # Extract unique banks and include the app package/name field
    df_bank = df_reviews[['bank_id', 'bank_name', 'app']].rename(columns={'app': 'app_name'})
    df_bank['app_name'] = df_bank['app_name'].fillna(df_bank['bank_name'])
    df_bank = df_bank.drop_duplicates(subset=['bank_id'])

    return df_reviews, df_bank


def insert_to_db(df_reviews: pd.DataFrame, df_bank: pd.DataFrame, db_config: dict) -> None:
    """Connect to database, insert banks, then insert reviews."""
    logger.info("Connecting to PostgreSQL database '%s' at %s ...", db_config['database'], db_config['host'])
    
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    try:
        # --- Insert Banks ---
        logger.info("Inserting unique banks into the 'banks' table...")
        for _, row in df_bank.iterrows():
            cur.execute(
                """
                INSERT INTO banks (bank_id, bank_name, app_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (bank_id) DO UPDATE SET bank_name = EXCLUDED.bank_name, app_name = EXCLUDED.app_name;
                """,
                (int(row["bank_id"]), row["bank_name"], row["app_name"])
            )
        logger.info("Successfully populated banks table (count: %d).", len(df_bank))

        # --- Insert Reviews ---
        logger.info("Inserting reviews into the 'reviews' table...")
        inserted_count = 0
        for _, row in df_reviews.iterrows():
            cur.execute(
                """
                INSERT INTO reviews (review_id, bank_id, review_text, sentiment_label, sentiment_score, identified_theme, rating, review_date, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (review_id) DO NOTHING;
                """,
                (
                    int(row["review_id"]),
                    int(row["bank_id"]),
                    row["review_text"],
                    row["sentiment_label"],
                    float(row["sentiment_score"]),
                    row["identified_theme"],
                    int(row["rating"]),
                    row["review_date"],
                    row["source"]
                )
            )
            inserted_count += 1

        conn.commit()
        logger.info("Successfully inserted %d reviews into the database.", inserted_count)

    except Exception as e:
        conn.rollback()
        logger.error("Database insertion failed. Transaction rolled back. Error: %s", e)
        raise e
    finally:
        cur.close()
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Insert processed bank reviews into database.")
    parser.add_argument("--clean-csv", type=Path, default=DEFAULT_CLEAN,
                        help=f"Path to cleaned reviews CSV (default: {DEFAULT_CLEAN})")
    parser.add_argument("--proc-csv", type=Path, default=DEFAULT_PROC,
                        help=f"Path to processed reviews CSV (default: {DEFAULT_PROC})")
    args = parser.parse_args()

    if not args.clean_csv.exists():
        logger.error("Cleaned bank reviews file not found: %s", args.clean_csv)
        sys.exit(1)

    df_reviews, df_bank = merge_and_prepare_data(args.clean_csv, args.proc_csv)
    insert_to_db(df_reviews, df_bank, DB_CONFIG)


if __name__ == "__main__":
    main()
