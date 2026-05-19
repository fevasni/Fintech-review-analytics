# 📊 Fintech Review Analytics

A data pipeline and NLP analysis toolkit for scraping, preprocessing, and performing sentiment & thematic analysis on customer reviews from Ethiopian fintech mobile banking applications (CBE, Dashen Bank, Bank of Abyssinia).

---

## 🚀 Project Overview

This project collects user reviews from mobile banking apps on the Google Play Store, applies NLP preprocessing (tokenization, stop-word removal, lemmatization), and derives sentiment scores and thematic insights using transformer-based models. Results are exported as structured CSVs and can be explored via a Streamlit dashboard.

**Key capabilities:**
- 🕷️ Automated review scraping per bank app
- 🧹 Modular NLP preprocessing pipeline
- 🤖 Transformer-based sentiment classification (HuggingFace `transformers`)
- 🏷️ Theme identification from review text
- 📈 Visualization with Matplotlib & Seaborn
- ✅ Unit-tested utilities with `pytest`

---

## 🗂️ Project Structure

```
fintech-review-analytics/
│
├── database/                           # Database schema definitions
│   └── schema.sql                     # PostgreSQL schema setup script
│
├── notebooks/                          # Jupyter notebooks for exploration & analysis
│   ├── BOA_scraping_preprocessing.ipynb       # Bank of Abyssinia — scraping & preprocessing
│   ├── CBE_scraping_preprocessing.ipynb       # CBE — scraping & preprocessing
│   ├── Dashen_scraping_preprocessing.ipynb    # Dashen Bank — scraping & preprocessing
│   ├── semantic_analysis.ipynb                # Sentiment & thematic analysis (main analysis)
│   ├── processed_reviews.csv                  # Cleaned & merged review dataset
│   └── data/                                  # Raw scraped data per bank
│
├── scripts/                            # Standalone Python scripts
│   ├── insert_reviews.py              # Script to load and insert reviews into DB
│   └── nlp_preprocessing.py           # Modular NLP pipeline (tokenize → clean → lemmatize)
│
├── src/                                # Reusable source modules
│   └── utils.py                       # Shared utility functions
│
├── tests/                              # Unit tests
│   └── test_example.py
│
├── .github/                            # CI/CD workflows
├── requirements.txt                    # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python **3.10+**
- `pip` and optionally a virtual environment manager

### 1. Clone the repository
```bash
git clone https://github.com/fevasni/Fintech-review-analytics.git
cd fintech-review-analytics
```

### 2. Create & activate a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root if API keys or configuration values are required:
```env
# Example
SOME_API_KEY=your_key_here
```

### 5. PostgreSQL Database Setup
To store scraped and analyzed bank reviews in PostgreSQL:
1. Ensure PostgreSQL is installed and running on your local machine.
2. Create a new database named `bank_review`:
   ```sql
   CREATE DATABASE bank_review;
   ```
3. Run the schema creation file to initialize the tables:
   ```bash
   psql -U your_username -d bank_review -f database/schema.sql
   ```
4. Insert the scraped and processed bank reviews into the database by running:
   ```bash
   python scripts/insert_reviews.py
   ```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `pandas` | 2.2.3 | Data manipulation |
| `numpy` | 2.2.3 | Numerical operations |
| `matplotlib` | 3.9.2 | Plotting |
| `seaborn` | 0.13.2 | Statistical visualizations |
| `scipy` | 1.14.1 | Statistical analysis |
| `transformers` | 4.41.2 | HuggingFace NLP models |
| `torch` | 2.3.1 | Deep learning backend |
| `tqdm` | 4.66.4 | Progress bars |
| `streamlit` | 1.41.1 | Interactive dashboard |
| `pytest` | 8.2.0 | Unit testing |
| `flake8` | 7.0.0 | Code linting |
| `python-dotenv` | 1.0.1 | Environment variable management |

---

## 🧪 Usage

### Run NLP Preprocessing
```bash
python scripts/nlp_preprocessing.py
```
Outputs a CSV with the following columns:

| Column | Description |
|---|---|
| `review_id` | Unique identifier for each review |
| `review_text` | Cleaned and preprocessed review text |
| `sentiment_label` | Predicted sentiment (`positive` / `negative` / `neutral`) |
| `sentiment_score` | Confidence score of the sentiment prediction |
| `identified_theme` | Key theme extracted from the review |

### Run the Notebooks
Launch JupyterLab or Jupyter Notebook:
```bash
jupyter lab
```
Open the notebooks in order:
1. `BOA_scraping_preprocessing.ipynb` — scrape & preprocess BOA reviews
2. `CBE_scraping_preprocessing.ipynb` — scrape & preprocess CBE reviews
3. `Dashen_scraping_preprocessing.ipynb` — scrape & preprocess Dashen reviews
4. `semantic_analysis.ipynb` — run sentiment & thematic analysis

### Run Tests
```bash
pytest tests/
```

### Lint the Code
```bash
flake8 scripts/ src/
```

---

## 📊 Output

The processed dataset (`notebooks/processed_reviews.csv`) contains merged and cleaned reviews across all three banks, ready for analysis and visualization.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is for academic and research purposes. See [LICENSE](LICENSE) for details.
