"""
scripts/preprocessor.py
========================
Data-cleaning pipeline for scraped Google Play reviews.

Implements every step that was previously hand-coded inside three separate
Jupyter notebooks:
  - NaN / missing-value handling for review text and ratings
  - Review-ID–based duplicate removal (primary key deduplication)
  - Date normalisation  →  ISO 8601 'YYYY-MM-DD' strings
  - Review-text whitespace normalisation
  - Rating range validation  (1 – 5)

Public API
----------
preprocess(df)                     -> pd.DataFrame   (main pipeline)
handle_missing_values(df)          -> pd.DataFrame
remove_duplicates_by_id(df)        -> pd.DataFrame
normalize_dates(df)                -> pd.DataFrame
clean_review_text(df)              -> pd.DataFrame
validate_ratings(df)               -> pd.DataFrame
"""

from __future__ import annotations

import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Individual pipeline steps
# ---------------------------------------------------------------------------

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows where *review* text or *rating* is NaN / None.

    These are the two critical fields; rows missing either are unusable for
    any downstream NLP or sentiment analysis.

    Parameters
    ----------
    df : Raw DataFrame produced by the scraper (must contain 'review' and
         'rating' columns).

    Returns
    -------
    A copy of *df* with incomplete rows removed.
    """
    before = len(df)
    critical_cols = ["review", "rating"]
    df = df.dropna(subset=critical_cols).copy()
    removed = before - len(df)
    if removed:
        logger.warning(
            "handle_missing_values: dropped %d rows with NaN review/rating.", removed
        )
    else:
        logger.info("handle_missing_values: no missing values found.")
    return df


def remove_duplicates_by_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows using *review_id* as the primary key.

    Google Play sometimes returns the same review in multiple API calls.
    Deduplication on the unique review ID is the correct approach (as opposed
    to fuzzy-matching on text, which can incorrectly discard distinct reviews
    that happen to share a common short phrase like "good app").

    Parameters
    ----------
    df : DataFrame that must contain a 'review_id' column.

    Returns
    -------
    DataFrame with the first occurrence of each review_id kept.
    """
    before = len(df)
    df = df.drop_duplicates(subset=["review_id"], keep="first").copy()
    removed = before - len(df)
    if removed:
        logger.info(
            "remove_duplicates_by_id: removed %d duplicate review IDs.", removed
        )
    else:
        logger.info("remove_duplicates_by_id: no duplicate IDs found.")
    return df


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise the *date* column to ISO 8601 'YYYY-MM-DD' strings.

    The scraper returns Python ``datetime`` objects (stored as
    ``datetime64[ns]`` by pandas).  This step strips the time component and
    formats the result as a plain date string so downstream code and CSV
    exports are unambiguous and human-readable.

    Parameters
    ----------
    df : DataFrame with a 'date' column (datetime or string).

    Returns
    -------
    DataFrame with 'date' column as object dtype 'YYYY-MM-DD' strings.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    # Log rows where conversion produced NaT (now the string "NaT")
    bad_dates = df["date"].isna().sum()
    if bad_dates:
        logger.warning(
            "normalize_dates: %d rows had un-parseable dates; set to NaT.", bad_dates
        )
    else:
        logger.info("normalize_dates: all dates normalised successfully.")
    return df


def _clean_text(text) -> str:
    """
    Collapse whitespace and strip leading/trailing space from a single value.

    Returns an empty string for NaN inputs so the caller can filter them out.
    """
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"\s+", " ", text)  # collapse tabs / newlines / multiple spaces
    return text.strip()


def clean_review_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise whitespace in the *review* column; drop rows that become empty.

    NaN values in the review column are converted to empty strings by
    ``_clean_text``, then the subsequent length filter removes them, ensuring
    every remaining row has a non-empty, whitespace-normalised review.

    Parameters
    ----------
    df : DataFrame with a 'review' column.

    Returns
    -------
    DataFrame with cleaned, non-empty review texts.
    """
    df = df.copy()
    df["review"] = df["review"].apply(_clean_text)

    before = len(df)
    df = df[df["review"].str.len() > 0].copy()
    removed = before - len(df)
    if removed:
        logger.info(
            "clean_review_text: removed %d rows that were empty after cleaning.",
            removed,
        )
    else:
        logger.info("clean_review_text: no empty reviews after cleaning.")
    return df


def validate_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only rows where *rating* is in the valid range [1, 5] and cast to int.

    Google Play ratings are always integers 1–5, but network errors or future
    API changes could introduce out-of-range floats.  This step makes the
    constraint explicit and enforced.

    Parameters
    ----------
    df : DataFrame with a numeric 'rating' column.

    Returns
    -------
    DataFrame filtered to valid ratings stored as Python int (int64).
    """
    df = df.copy()
    before = len(df)
    df = df[(df["rating"] >= 1) & (df["rating"] <= 5)].copy()
    removed = before - len(df)
    if removed:
        logger.warning(
            "validate_ratings: removed %d rows with out-of-range ratings.", removed
        )
    else:
        logger.info("validate_ratings: all ratings in valid range [1, 5].")
    df["rating"] = df["rating"].astype(int)
    return df


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the complete preprocessing pipeline on a raw reviews DataFrame.

    Steps (in order):
        1. handle_missing_values   – drop rows with NaN review or rating
        2. remove_duplicates_by_id – deduplicate on review_id (primary key)
        3. normalize_dates         – convert datetime → 'YYYY-MM-DD' string
        4. clean_review_text       – collapse whitespace; drop empty reviews
        5. validate_ratings        – keep ratings 1-5; cast to int

    Parameters
    ----------
    df : Raw DataFrame returned by ``scraper.scrape_to_dataframe()`` or
         equivalent.  Expected columns:
            review_id, review, rating, date, bank, source

    Returns
    -------
    Clean DataFrame with the same column structure but only valid rows.
    """
    logger.info("Starting preprocessing pipeline with %d rows.", len(df))

    df = handle_missing_values(df)
    df = remove_duplicates_by_id(df)
    df = normalize_dates(df)
    df = clean_review_text(df)
    df = validate_ratings(df)

    # Final column order
    output_cols = ["review_id", "review", "rating", "date", "bank", "source"]
    # Keep only the expected columns (guard against extra scraper fields)
    df = df[[c for c in output_cols if c in df.columns]].copy()
    df = df.reset_index(drop=True)

    logger.info("Preprocessing complete. Final dataset: %d rows.", len(df))
    return df
