"""
scripts/scraper.py
==================
Google Play review scraper for Ethiopian fintech apps.

Extracts the scraping logic that was previously duplicated across:
  - notebooks/BOA_scraping_preprocessing copy.ipynb
  - notebooks/CBE_scraping_preprocessing.ipynb
  - notebooks/Dashen_scraping_preprocessing copy.ipynb

Public API
----------
scrape_bank(app_id, bank_name, count, lang, country) -> list[dict]
scrape_all_banks(count, lang, country)               -> list[dict]
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
from google_play_scraper import Sort, app, reviews

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App identifiers (one place to update if package names ever change)
# ---------------------------------------------------------------------------
APP_IDS: dict[str, str] = {
    "BOA Bank": "com.boa.boaMobileBanking",
    "CBE Bank": "com.combanketh.mobilebanking",
    "Dashen Bank": "com.dashen.dashensuperapp",
}


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def fetch_app_info(app_id: str, lang: str = "en", country: str = "et") -> dict:
    """Return raw app metadata from the Play Store for logging/diagnostics."""
    return app(app_id, lang=lang, country=country)


def scrape_bank(
    app_id: str,
    bank_name: str,
    count: int = 500,
    lang: str = "en",
    country: str = "et",
) -> list[dict]:
    """
    Scrape up to *count* reviews for a single bank app.

    Parameters
    ----------
    app_id    : Google Play package name (e.g. 'com.boa.boaMobileBanking')
    bank_name : Human-readable label stored in the 'bank' column
    count     : Maximum number of reviews to fetch
    lang      : Language code passed to google_play_scraper
    country   : Country code passed to google_play_scraper

    Returns
    -------
    List of raw review dicts with keys:
        review_id, review, rating, date, bank, source
    """
    logger.info("Scraping %d reviews for %s (app_id=%s)…", count, bank_name, app_id)

    result, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,       # Most-recent first
        count=count,
        filter_score_with=None, # All star ratings
    )

    logger.info("  → Collected %d raw reviews for %s", len(result), bank_name)

    records: list[dict] = []
    for r in result:
        records.append(
            {
                "review_id": r.get("reviewId", ""),
                "review": r.get("content", ""),
                "rating": r.get("score", None),
                "date": r.get("at", None),
                "bank": bank_name,
                "source": "Google Play",
            }
        )
    return records


def scrape_all_banks(
    count: int = 500,
    lang: str = "en",
    country: str = "et",
    app_ids: Optional[dict[str, str]] = None,
) -> list[dict]:
    """
    Scrape reviews for **all** configured banks and return a combined list.

    Parameters
    ----------
    count    : Reviews per bank
    lang     : Language code
    country  : Country code
    app_ids  : Override the default APP_IDS mapping {bank_name: app_id}.
               Pass None to use the module-level defaults.

    Returns
    -------
    Flat list of raw review dicts ready for the preprocessor.
    """
    ids = app_ids if app_ids is not None else APP_IDS
    all_records: list[dict] = []

    for bank_name, app_id in ids.items():
        bank_records = scrape_bank(
            app_id=app_id,
            bank_name=bank_name,
            count=count,
            lang=lang,
            country=country,
        )
        all_records.extend(bank_records)
        logger.info("Running total: %d reviews collected so far.", len(all_records))

    logger.info("Scraping complete. Total raw reviews: %d", len(all_records))
    return all_records


# ---------------------------------------------------------------------------
# Convenience: build a raw DataFrame directly
# ---------------------------------------------------------------------------

def scrape_to_dataframe(
    count: int = 500,
    lang: str = "en",
    country: str = "et",
    app_ids: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """Scrape all banks and return a raw (un-preprocessed) DataFrame."""
    records = scrape_all_banks(count=count, lang=lang, country=country, app_ids=app_ids)
    return pd.DataFrame(records)
