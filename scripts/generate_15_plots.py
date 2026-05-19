import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)

ROOT = Path(__file__).resolve().parent.parent
PLOTS_DIR = ROOT / 'notebooks' / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

CLEANED_PATH = ROOT / 'notebooks' / 'data' / 'processed' / 'cleaned_bank_reviews.csv'
PROCESS_PATH = ROOT / 'notebooks' / 'processed_reviews.csv'


def load_data():
    df = pd.read_csv(CLEANED_PATH, parse_dates=['date'])
    df = df.rename(columns={'bank_name': 'bank'})
    df['review_len'] = df['review'].astype(str).str.len()
    df['review_word_count'] = df['review'].astype(str).str.split().apply(len)
    return df


def compute_sentiment(df):
    analyzer = SentimentIntensityAnalyzer()
    scores = df['review'].astype(str).apply(analyzer.polarity_scores)
    scores_df = pd.DataFrame(scores.tolist())
    df = pd.concat([df.reset_index(drop=True), scores_df], axis=1)
    df['sentiment_label'] = np.where(df['compound'] >= 0.05, 'positive', np.where(df['compound'] <= -0.05, 'negative', 'neutral'))
    return df


def save_plot(fig, filename):
    path = PLOTS_DIR / filename
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def plot_review_count_by_bank(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.countplot(data=df, x='bank', order=df['bank'].value_counts().index, palette='Set2', ax=ax)
    ax.set_title('Total Reviews by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Bank App')
    ax.set_ylabel('Review Count')
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10)
    save_plot(fig, 'review_count_by_bank.png')


def plot_rating_distribution_by_bank(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df, x='rating', hue='bank', palette='Set1', dodge=True, ax=ax)
    ax.set_title('Rating Distribution by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Number of Reviews')
    save_plot(fig, 'rating_distribution_by_bank.png')


def plot_average_rating_by_bank(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    avg = df.groupby('bank')['rating'].mean().sort_values(ascending=False)
    sns.barplot(x=avg.index, y=avg.values, palette='Blues', ax=ax)
    ax.set_title('Average Rating by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Bank App')
    ax.set_ylabel('Average Rating')
    ax.set_ylim(0, 5)
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10)
    save_plot(fig, 'average_rating_by_bank.png')


def plot_star_share_by_bank(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    prop = df.groupby(['bank', 'rating']).size().groupby(level=0).apply(lambda x: x / x.sum()).unstack().fillna(0)
    prop.plot(kind='bar', stacked=True, colormap='tab20', ax=ax)
    ax.set_title('Star Rating Share by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Bank App')
    ax.set_ylabel('Share of Reviews')
    ax.legend(title='Rating', bbox_to_anchor=(1.05, 1), loc='upper left')
    save_plot(fig, 'star_rating_share_by_bank.png')


def plot_weekly_review_volume(df):
    df2 = df.set_index('date').groupby('bank').resample('W').size().reset_index(name='count')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df2, x='date', y='count', hue='bank', marker='o', ax=ax)
    ax.set_title('Weekly Review Volume by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Week')
    ax.set_ylabel('Review Count')
    save_plot(fig, 'weekly_review_volume.png')


def plot_rating_trend(df):
    df2 = df.set_index('date').groupby('bank')['rating'].resample('W').mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df2, x='date', y='rating', hue='bank', marker='o', ax=ax)
    ax.set_title('Weekly Average Rating Trend by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Week')
    ax.set_ylabel('Average Rating')
    ax.set_ylim(1, 5)
    save_plot(fig, 'weekly_average_rating_trend.png')


def plot_review_length_distribution(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.kdeplot(data=df, x='review_len', hue='bank', fill=True, common_norm=False, alpha=0.4, ax=ax)
    ax.set_title('Review Length Distribution by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Review Length (characters)')
    ax.set_ylabel('Density')
    save_plot(fig, 'review_length_distribution.png')


def plot_sentiment_label_distribution(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df, x='sentiment_label', hue='bank', palette='Set2', ax=ax)
    ax.set_title('VADER Sentiment Label Distribution by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Review Count')
    save_plot(fig, 'sentiment_label_distribution_by_bank.png')


def plot_compound_score_boxplot(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x='bank', y='compound', palette='pastel', ax=ax)
    ax.set_title('VADER Compound Score by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Bank App')
    ax.set_ylabel('Compound Sentiment Score')
    save_plot(fig, 'vader_compound_by_bank.png')


def plot_rating_vs_compound(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x='rating', y='compound', hue='bank', alpha=0.7, ax=ax)
    ax.set_title('Rating vs. VADER Compound Score', fontsize=14, fontweight='bold')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Compound Score')
    save_plot(fig, 'rating_vs_compound_scatter.png')


def plot_avg_compound_by_rating(df):
    pivot = df.groupby(['bank', 'rating'])['compound'].mean().unstack()
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind='bar', ax=ax, colormap='Set3')
    ax.set_title('Average VADER Compound Score by Rating and Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Bank App')
    ax.set_ylabel('Average Compound Score')
    ax.legend(title='Rating', bbox_to_anchor=(1.05, 1), loc='upper left')
    save_plot(fig, 'avg_compound_by_rating_bank.png')


def plot_sentiment_label_by_rating(df):
    df2 = df.groupby(['rating', 'sentiment_label']).size().groupby(level=0).apply(lambda x: x / x.sum()).unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(10, 6))
    df2.plot(kind='bar', stacked=True, colormap='Paired', ax=ax)
    ax.set_title('Sentiment Share by Rating', fontsize=14, fontweight='bold')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Share of Reviews')
    ax.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
    save_plot(fig, 'sentiment_label_share_by_rating.png')


def plot_top_ngrams(df, ngram_range=(1, 1), top_n=10, filename='top_unigrams.png', title='Top Unigrams by Bank'):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=False)
    banks = sorted(df['bank'].unique())
    for i, bank in enumerate(banks):
        bank_reviews = df.loc[df['bank'] == bank, 'clean_text'].astype(str)
        vectorizer = CountVectorizer(ngram_range=ngram_range, stop_words='english', min_df=2)
        X = vectorizer.fit_transform(bank_reviews)
        freqs = np.asarray(X.sum(axis=0)).ravel()
        terms = np.array(vectorizer.get_feature_names_out())
        top_idx = freqs.argsort()[::-1][:top_n]
        words = terms[top_idx]
        counts = freqs[top_idx]
        sns.barplot(x=counts, y=words, palette='viridis', ax=axes[i])
        axes[i].set_title(bank)
        axes[i].set_xlabel('Count')
        axes[i].set_ylabel('')
    plt.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_plot(fig, filename)


def main():
    df = load_data()
    df = compute_sentiment(df)
    plot_review_count_by_bank(df)
    plot_rating_distribution_by_bank(df)
    plot_average_rating_by_bank(df)
    plot_star_share_by_bank(df)
    plot_weekly_review_volume(df)
    plot_rating_trend(df)
    plot_review_length_distribution(df)
    plot_sentiment_label_distribution(df)
    plot_compound_score_boxplot(df)
    plot_rating_vs_compound(df)
    plot_avg_compound_by_rating(df)
    plot_sentiment_label_by_rating(df)
    plot_top_ngrams(df, ngram_range=(1, 1), top_n=10, filename='top_unigrams_by_bank.png', title='Top Unigrams by Bank')
    plot_top_ngrams(df, ngram_range=(2, 2), top_n=10, filename='top_bigrams_by_bank.png', title='Top Bigrams by Bank')
    plot_top_ngrams(df, ngram_range=(3, 3), top_n=10, filename='top_trigrams_by_bank.png', title='Top Trigrams by Bank')

if __name__ == '__main__':
    main()
