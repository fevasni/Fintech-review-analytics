import json

notebook_path = r'c:\Users\PC\Documents\New folder (2)\fintech-review-analytics\notebooks\semantic_analysis.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cell_code = """# Cell: Modular Preprocessing and Export
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os
import re

def process_text_modular(text, apply_lemmatization=True):
    \"\"\"
    Handles tokenization, stop-word removal, and optional lemmatization.
    \"\"\"
    if pd.isna(text):
        return ""
    
    # Cleaning
    text = re.sub(r'[^a-zA-Z\s]', ' ', str(text).lower())
    
    # Tokenization
    tokens = word_tokenize(text)
    
    # Stop-word removal
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Optional Lemmatization
    if apply_lemmatization:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        
    return " ".join(tokens)

# Apply the preprocessing
df_clean['processed_text'] = df_clean['review'].apply(lambda x: process_text_modular(x, apply_lemmatization=True))

# Prepare the final dataframe with requested columns
# review_id, review_text, sentiment_label, sentiment_score, identified_theme
df_export = pd.DataFrame()

# Assuming review_id can be generated if not present
if 'review_id' in df_clean.columns:
    df_export['review_id'] = df_clean['review_id']
else:
    df_export['review_id'] = df_clean.index + 1
    
df_export['review_text'] = df_clean['review']

if 'sentiment' in df_clean.columns:
    df_export['sentiment_label'] = df_clean['sentiment']
else:
    df_export['sentiment_label'] = 'Neutral'
    
if 'vader_compound' in df_clean.columns:
    df_export['sentiment_score'] = df_clean['vader_compound']
else:
    df_export['sentiment_score'] = 0.0

# Using identified_theme if available, else 'General'
if 'theme' in df_clean.columns:
    df_export['identified_theme'] = df_clean['theme']
else:
    df_export['identified_theme'] = 'General'

# Save to CSV
output_csv = 'processed_reviews.csv'
df_export.to_csv(output_csv, index=False)
print(f"Results saved to {output_csv}")
"""

new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "new_modular_cell",
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" for line in new_cell_code.split('\n')]
}

# The last line should not have a trailing newline
new_cell['source'][-1] = new_cell['source'][-1][:-1]

# Append the new cell
nb['cells'].append(new_cell)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
    
print("Notebook modified successfully.")
