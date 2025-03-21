from collections import Counter
import re
import pandas as pd
import numpy as np

def get_common_words(df, column_name):
    text = ' '.join(df[column_name].dropna().astype(str))
    words = re.findall(r'\b(?!\d{1,2}\b)[a-zA-Z0-9]{2,}\b', text.lower())
    word_counts = Counter(words)
    top_10_percent = int(len(word_counts) * 0.1) or 1
    return [word for word, _ in word_counts.most_common(top_10_percent)]

def pattern_clustering(df, column_name, threshold=1.0):
    cluster_id_column = f"{column_name}_Cluster_ID"
    percentage_column = f"{column_name}_Cluster_Percentage"
    
    result_df = df[[column_name]].copy()
    result_df[column_name] = result_df[column_name].fillna("")  # Treat NaN as empty string
    
    # Assign cluster IDs
    result_df[cluster_id_column] = result_df.groupby(column_name).ngroup()
    
    # Calculate percentages
    pattern_counts = result_df[column_name].value_counts(normalize=True) * 100
    
    result_df[percentage_column] = result_df[column_name].map(pattern_counts)
    
    # Exclude empty strings from low-coverage patterns
    low_coverage_patterns = pattern_counts[(pattern_counts < threshold) & (pattern_counts.index != "")].index.tolist()
    
    # Only flag non-empty rows
    mask = result_df[column_name] != ""
    pattern_issues = result_df[mask & result_df[column_name].isin(low_coverage_patterns)].index.tolist()
    
    pattern_percentage_dict = pattern_counts.to_dict()
    
    row_issues = {}
    invalid = mask & result_df[column_name].isin(low_coverage_patterns)
    issues = np.where(
        invalid,
        f"Pattern coverage below {threshold}% threshold",
        ""
    )
    index = 0
    while index < len(issues):
        if issues[index]:
            row_issues[index] = [issues[index]]
        index += 1
    
    return pattern_issues, result_df, pattern_percentage_dict, row_issues

def main():
    data = {
        'text_column': [
            'AB1234567', 'CD9876543', 'AB1234567', 'XY7654321', 
            'A123456', 'BC12XYZ89', 'EF4567890', 'G123', 'KL5432109', 
            'MN12', 'AB12345XY', '', None
        ]
    }
    df = pd.DataFrame(data)
    common_words = get_common_words(df, 'text_column')
    print("Top 10% common words:", common_words)
    print("\n")
    pattern_issues, result_df, pattern_percentage_dict, row_issues = pattern_clustering(df, 'text_column', threshold=10.0)  # Adjusted threshold for demo
    print("Pattern Issues (Low coverage indexes):", pattern_issues)
    print("\nUpdated DataFrame (result_df):")
    print(result_df)
    print("\nPattern-Percentage Dictionary:", pattern_percentage_dict)
    print("\nRow-wise Pattern Issues:", row_issues)

if __name__ == "__main__":
    main()