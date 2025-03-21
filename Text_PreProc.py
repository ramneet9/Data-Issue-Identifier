"""Handles text preprocessing and pattern clustering."""

import pandas as pd
import nltk
import re
from collections import Counter
from fuzzywuzzy import process


def load_excel(file_path):
    """
    Load an Excel file into a DataFrame.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    df = pd.read_excel(file_path, engine="calamine")
    df.columns = df.columns.str.strip()
    return df

def match_cols(df_cols, expected):
    """
    Match DataFrame columns to expected column names using fuzzy matching.

    Args:
        df_cols (Index): DataFrame column names.
        expected (dict): Dictionary of expected column names and their variations.

    Returns:
        dict: Dictionary mapping expected names to actual column names.
    """
    matched = {}
    i = 0
    while i < len(df_cols):
        col = df_cols[i]
        j = 0
        while j < len(expected):
            key = list(expected.keys())[j]
            best, score = process.extractOne(col, expected[key])
            if score >= 80:
                matched[key] = col
                break
            j += 1
        i += 1
    return matched

# Initialize stopwords once at module level
nltk.download('stopwords', quiet=True)
stop_words = set(nltk.corpus.stopwords.words('english'))

def preprocess_text(df, col):
    """
    Preprocess text in a DataFrame column by lowercasing, removing stopwords, and cleaning.

    Args:
        df (pd.DataFrame): Input DataFrame.
        col (str): Column name to process.

    Returns:
        pd.DataFrame: DataFrame with processed text column.
    """
    # Convert column to object dtype to avoid dtype mismatch
    df[col] = df[col].astype(str)
    
    i = 0
    while i < len(df):
        text = str(df.at[i, col]).lower()
        words = text.split()
        j = 0
        filtered = []
        while j < len(words):
            if words[j] not in stop_words:
                filtered.append(words[j])
            j += 1
        text = " ".join(filtered)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[-*#]', ' ', text)
        df.at[i, col] = text
        i += 1
    return df

def get_common_words(df, col):
    """
    Extract the top 10% most common words from a column, excluding short numbers.

    Args:
        df (pd.DataFrame): Input DataFrame.
        col (str): Column name to analyze.

    Returns:
        list: List of common words.
    """
    text = " ".join(df[col].dropna().astype(str))
    words = re.findall(r'\b(?!\d{1,2}\b)[a-zA-Z]{2,}|\d{3,}\b', text.lower())
    counts = Counter(words)
    top_10 = int(len(counts) * 0.1) or 1
    common = []
    i = 0
    items = counts.most_common()
    while i < top_10 and i < len(items):
        common.append(items[i][0])
        i += 1
    return common

def replace_words(text, common):
    """
    Replace words in text with patterns (e.g., 'CW' for common words).

    Args:
        text (str): Input text.
        common (list): List of common words.

    Returns:
        str: Processed text with replacements.
    """
    def transform(word):
        if word in common:
            return "CW"
        if word.isalpha():
            return f"t{len(word)}"
        if word.isdigit():
            return f"n{len(word)}"
        if any(c.isalpha() for c in word) and any(c.isdigit() for c in word):
            text_part = "".join(c for c in word if c.isalpha())
            num_part = "".join(c for c in word if c.isdigit())
            return f"t{len(text_part)}n{len(num_part)}"
        return word
    words = re.findall(r'\w+', text)
    i = 0
    result = []
    while i < len(words):
        result.append(transform(words[i]))
        i += 1
    return " ".join(result)

def normalize_pattern(text):
    """
    Normalize text by replacing tX and nX patterns.

    Args:
        text (str): Input text.

    Returns:
        str: Normalized text.
    """
    text = re.sub(r'\bt\d+\b', 'tX', text)
    text = re.sub(r'\bn\d+\b', 'nX', text)
    return text
