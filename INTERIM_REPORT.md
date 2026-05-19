# Interim Progress Report: Ethiopian Fintech Review Analytics
**Omega Consultancy – CBE, BOA, and Dashen Bank Engagement**

---

## Executive Summary

Omega Consultancy has been engaged to deliver a comprehensive Google Play Store review analytics solution for three of Ethiopia's leading financial institutions: Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank. This interim report documents progress through a four-part analysis pipeline designed to transform unstructured user feedback into actionable competitive intelligence assets.

**Current Status:** Task 1 (Data Collection and Preprocessing) completed successfully. Task 2 (Sentiment and Thematic Analysis) is in progress with initial sentiment classification and theme identification completed. Tasks 3 (Database Engineering) and 4 (Insights and Recommendations) remain pending.

---

## 1. Business Objective and Strategic Context

### 1.1 Engagement Scope

Omega Consultancy is partnering with CBE, BOA, and Dashen Bank to leverage Google Play Store review analytics as a strategic competitive intelligence tool in Ethiopia's rapidly evolving fintech landscape. As mobile banking adoption accelerates, user feedback from app stores represents a critical, real-time signal of product performance and competitive positioning.

### 1.2 Why Google Play Store Review Analytics Matters

Ethiopia's fintech sector is experiencing unprecedented growth, with mobile banking apps becoming the primary interface for millions of customers. Unlike traditional customer satisfaction surveys—which are infrequent, expensive, and suffer from low response rates—Google Play Store reviews provide real-time, high-volume, unfiltered sentiment at no additional cost. For Ethiopian banks competing in a digital-first market, understanding and acting on this feedback is essential for customer retention, product improvement, and market differentiation.

### 1.3 Four-Part Analysis Pipeline

The project employs a structured four-phase approach:

1. **Data Collection and Preprocessing**: Automated scraping using google-play-scraper, followed by rigorous data cleaning and normalization
2. **Sentiment and Thematic Analysis**: Application of multiple NLP models (VADER, TextBlob, Transformer-based) to classify sentiment and identify key themes
3. **Database Engineering**: PostgreSQL schema design with banks and reviews tables, enabling efficient querying and analysis
4. **Insights and Recommendations**: Bank-specific satisfaction drivers, pain points, stakeholder-ready visualizations, and concrete product recommendations

### 1.4 Value Proposition

Transforming unstructured user feedback into competitive intelligence enables bank product teams to identify critical pain points, track sentiment trends over time, benchmark performance against competitors, inform product roadmaps with data-driven feature prioritization, and demonstrate customer-centricity to stakeholders with quantitative evidence.

---

## 2. Completed Work: Task 1 – Data Collection and Preprocessing

### 2.1 Scraping Methodology

The project utilizes the `google-play-scraper` Python library for extracting Google Play Store review data without requiring API keys. Implementation includes:

- **App Package Identifiers**: BOA (`com.boa.boaMobileBanking`), CBE (`com.combanketh.mobilebanking`), Dashen (`com.dashen.dashensuperapp`)
- **Scraping Parameters**: Language: English, Country: Ethiopia, Sort: Most recent first, Review Count: 250 per bank
- **Data Fields Extracted**: review_id, review content, star rating (1-5), date, thumbs-up count
- **Modular Architecture**: Scraping logic extracted into reusable scripts (`scripts/scraper.py`, `scripts/scrape_reviews.py`)

### 2.2 Data Quality Outcomes

**Collection Results**:
- Total Raw Reviews: 750 (250 per bank)
- Final Cleaned Dataset: 728 reviews
- Data Retention Rate: 97.1% (high initial data quality)

**Per-Bank Breakdown**:
- BOA: 250 raw → 248 cleaned (99.2% retention)
- CBE: 250 raw → 242 cleaned (96.8% retention)
- Dashen: 250 raw → 238 cleaned (95.2% retention)

**Missing Data Analysis**: 0% missing in critical fields (review text, rating). 22 duplicate reviews removed using review_id as primary key. Reviews with empty text or out-of-range ratings filtered during preprocessing.

### 2.3 Preprocessing Pipeline

The preprocessing pipeline (`scripts/preprocessor.py`) implements a five-step cleaning process:

1. **Missing Value Handling**: Drop rows where review text or rating is NaN/None
2. **Deduplication**: Remove duplicate rows using review_id as primary key
3. **Date Normalization**: Convert datetime objects to ISO 8601 format (YYYY-MM-DD)
4. **Text Cleaning**: Collapse whitespace, strip leading/trailing spaces, drop empty reviews
5. **Rating Validation**: Ensure ratings are within valid range [1, 5] and cast to integer

**Additional NLP Preprocessing**: Text lowercasing, special character removal, NLTK tokenization, stop-word removal, WordNetLemmatizer lemmatization, minimum length filtering (tokens > 2 characters).

### 2.4 Rate-Limiting and Availability

No rate-limiting issues encountered during initial data collection. For larger-scale collection (1,000+ reviews per bank), recommended mitigation strategies include exponential backoff between requests, random delays (1-3 seconds) between bank scrapes, rotating user agents if IP-based restrictions emerge, and scheduling collection during off-peak hours. All three bank apps were accessible on the Google Play Store at the time of scraping.

---

## 3. Initial Analysis: Task 2 – Sentiment and Thematic Analysis

### 3.1 Sentiment Classification Approach

The project employs a multi-model sentiment analysis strategy:

- **VADER**: Rule-based sentiment analysis optimized for social media text, compound score ranges from -1 to +1, classification thresholds: positive (≥0.05), neutral (-0.05 to 0.05), negative (≤-0.05)
- **TextBlob**: Machine learning-based sentiment analysis, provides polarity (-1 to +1) and subjectivity (0 to 1) scores
- **Transformer-Based (DistilBERT)**: Deep learning model fine-tuned on SST-2 sentiment dataset, binary classification (POSITIVE/NEGATIVE) with confidence scores

### 3.2 Sentiment Distribution Results

**VADER Sentiment Distribution** (n=728): Positive 62% (451), Neutral 24% (175), Negative 13% (102)

**Transformer Sentiment Distribution** (n=728): POSITIVE 65% (473), NEGATIVE 35% (255)

The transformer model shows slightly higher positive classification (65% vs 62%), likely due to its ability to capture nuanced positive language. Strong positive sentiment across all three banks indicates generally satisfactory user experiences.

### 3.3 Sentiment vs. Star Rating Correlation

Analysis reveals strong correlation between sentiment scores and star ratings:

- 5-star: VADER +0.42, Transformer +0.73
- 4-star: VADER +0.26, Transformer +0.16
- 3-star: VADER +0.19, Transformer -0.22
- 2-star: VADER +0.06, Transformer -0.59
- 1-star: VADER -0.12, Transformer -0.75

CBE shows the strongest correlation between high ratings and positive sentiment, while BOA shows more variability in mid-range ratings (3-4 stars).

### 3.4 Thematic Analysis Methodology

Three complementary approaches: (1) TF-IDF Keyword Extraction for distinctive terms and bigrams/trigrams, (2) NMF Topic Modeling for automated topic discovery (4 topics per bank), (3) Bank-Specific Theme Mapping with manual keyword grouping into business-relevant categories (3-5 themes per bank).

### 3.5 Identified Themes by Bank

**BOA**: Account Access (12), App Performance (17), Transaction Issues (6), User Experience (4), Other (209)

**CBE**: Transaction Performance (17), UI & Design (13), Customer Support (7), Account Access (2), Other (198)

**Dashen**: Account Access (16), Transaction Issues (15), Feature Requests (14), App Stability (2), Other (196)

### 3.6 Visualization: Rating Distribution by Bank

![Rating Distribution per App](notebooks/rating_distribution.png)

**Figure 1**: Rating distribution across three banks shows similar patterns with concentration of 5-star ratings, indicating overall user satisfaction. Dashen shows highest proportion of 5-star reviews, while CBE has more balanced distribution across rating levels.

### 3.7 Visualization: Theme Sentiment Analysis

![Theme Sentiment Analysis](notebooks/theme_sentiment.png)

**Figure 2**: Average sentiment score by theme. Red bars indicate negative sentiment (pain points), blue bars indicate positive sentiment (satisfaction drivers). Account Access shows strongly negative sentiment (-0.67 to -0.99), indicating critical authentication issues. Transaction Performance shows mixed sentiment with CBE experiencing negative scores (-0.53). Customer Support shows positive sentiment for CBE (+0.99). Feature Requests shows mildly negative sentiment (-0.15).

### 3.8 Visualization: Top Keywords by Bank

![Keyword Analysis](notebooks/keyword_analysis.png)

**Figure 3**: TF-IDF top keywords by bank. Common positive terms across all banks include "good," "app," "best," and "nice." Bank-specific terms: BOA—"fast," "banking," "boa"; CBE—"update," "excellent," "transfer"; Dashen—"super," "dashen bank," "great."

---

## 4. Next Steps and Key Areas of Focus

### 4.1 Task 2 Completion

**Status**: Sentiment coverage at 100% (728/728 reviews), exceeding 90% target. Theme identification at 4 per bank, meeting 3+ requirement.

**Remaining Work**: Theme refinement to reduce "Other" category (currently 83% of reviews). Expand keyword dictionaries, implement zero-shot classification, cross-validate with product teams.

**Timeline**: 1-2 weeks

**Blocker/Mitigation**: High proportion of "Other" category indicates limited theme coverage. Mitigation: Expand theme mapping to include additional categories ("General Praise," "General Complaints," "Feature Usage"). Alternative: Implement unsupervised clustering (K-means on TF-IDF vectors).

### 4.2 Task 3: Database Engineering

**Planned Activities**: PostgreSQL schema design with `banks` table (bank_id, bank_name, app_package_id, created_at) and `reviews` table (review_id, bank_id foreign key, review_text, rating, date, sentiment_label, sentiment_score, identified_theme, thumbs_up_count, created_at). Indexes on bank_id, date, sentiment_label, identified_theme. SQLAlchemy ORM for data insertion with batch processing (100-500 records per batch), error handling, and upsert logic for duplicate review_ids.

**Timeline**: 1 week

**Blocker/Mitigation**: PostgreSQL environment not yet provisioned. Mitigation: Use Docker for local development; coordinate with IT team for production. Alternative: Implement SQLite for initial development, migrate to PostgreSQL for production.

### 4.3 Task 4: Insights and Recommendations

**Deliverables**: Bank-specific satisfaction drivers (CBE: customer support, strong features; BOA: fast performance, brand loyalty; Dashen: app stability, user-friendly interface). Bank-specific pain points (CBE: transaction delays, UI/UX; BOA: account access, app crashes; Dashen: login authentication, transaction failures). 3-5 stakeholder-ready visualizations (sentiment trend over time, theme distribution comparison, rating vs. sentiment scatter, competitive benchmarking dashboard, word clouds). Concrete product recommendations per bank.

**Timeline**: 2-3 weeks

**Blocker/Mitigation**: Limited historical data (single snapshot). Mitigation: Establish ongoing data collection pipeline for trend analysis; recommend quarterly refreshes.

### 4.4 Overall Project Timeline

- Task 2 refinement: 1-2 weeks
- Task 3 database engineering: 1 week
- Task 4 insights and recommendations: 2-3 weeks
- Final report and stakeholder presentation: 1 week

**Total Estimated Completion**: 5-7 weeks from interim report date

**Critical Path**: Task 3 (Database) → Task 4 (Insights) → Final Deliverables

---

## 5. Conclusion and Recommendations

### 5.1 Progress Assessment

The project has successfully completed foundational phases of data collection and initial sentiment analysis. High data quality (97.1% retention) and successful sentiment classification (100% coverage) provide solid foundation for advanced analysis. Thematic analysis identified key pain points and satisfaction drivers, though theme coverage requires refinement.

### 5.2 Key Findings

1. **Overall Positive Sentiment**: 62-65% of reviews express positive sentiment across all banks
2. **Critical Pain Point**: Account access issues show strongly negative sentiment across all banks
3. **Bank-Specific Strengths**: CBE excels in customer support, BOA demonstrates fast performance, Dashen shows strong app stability
4. **Theme Coverage Gap**: 83% of reviews fall into "Other" category, indicating need for expanded theme taxonomy

### 5.3 Immediate Next Steps

1. Expand theme mapping to reduce uncategorized reviews from 83% to <50%
2. Provision PostgreSQL environment for Task 3
3. Schedule stakeholder review with bank product teams
4. Establish ongoing automated weekly scraping

### 5.4 Strategic Recommendations

1. **Prioritize Account Access**: Consistently negative sentiment around login/authentication suggests highest priority for all three banks
2. **Leverage Competitive Intelligence**: Use comparative analysis to identify relative strengths/weaknesses; consider sharing best practices
3. **Institute Continuous Monitoring**: Establish as ongoing capability to track impact of product changes
4. **Close the Feedback Loop**: Consider implementing in-app feedback mechanisms alongside Play Store reviews

---

## Appendix: Technical Specifications

### A.1 Technology Stack

- **Scraping**: google-play-scraper (Python)
- **Data Processing**: pandas, numpy
- **NLP**: NLTK, TextBlob, transformers (HuggingFace)
- **Sentiment Models**: VADER, TextBlob, DistilBERT
- **Topic Modeling**: scikit-learn (TF-IDF, NMF)
- **Visualization**: matplotlib, seaborn
- **Database (Planned)**: PostgreSQL, SQLAlchemy
- **Version Control**: Git

### A.2 Data Schema (Planned)

```sql
CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    app_package_id VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    review_id VARCHAR(100) PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    date DATE NOT NULL,
    sentiment_label VARCHAR(20) NOT NULL,
    sentiment_score DECIMAL(5,4),
    identified_theme VARCHAR(100),
    thumbs_up_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX idx_reviews_date ON reviews(date);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment_label);
CREATE INDEX idx_reviews_theme ON reviews(identified_theme);
```

---

**Report Prepared By**: Omega Consultancy Data Analytics Team  
**Date**: May 17, 2026  
**Project**: Ethiopian Fintech Review Analytics  
**Clients**: Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), Dashen Bank  
**Status**: Interim Progress Report – Tasks 1-2 In Progress
