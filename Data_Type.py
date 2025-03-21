import pandas as pd
import numpy as np
from datetime import datetime
import re

def dtype(df, expected_dtypes, matched_cols=None):
    """
    Validate data types for columns based on expected types and return error indices and row-wise issues.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        expected_dtypes (dict): Dictionary of expected column names and their data types
        matched_cols (dict): Mapping of expected column names to actual column names
        
    Returns:
        tuple: (error_indices, row_issues)
            - error_indices: dict mapping column names to lists of row indices with errors
            - row_issues: dict mapping row indices to lists of issue descriptions
    """
    error_indices = {col: [] for col in matched_cols.values()} if matched_cols else {}
    row_issues = {}

    if not matched_cols:
        return error_indices, row_issues

    for expected_col, actual_col in matched_cols.items():
        if expected_col in expected_dtypes:
            expected_type = expected_dtypes[expected_col]

            # DATE: Check for valid date format
            if expected_type == "date":
                # Preprocess to handle list-like strings
                def clean_date(value):
                    if pd.isna(value) or value == "" or value == "[]":
                        return pd.NA
                    str_val = str(value).strip()
                    match = re.match(r"\['([^']+)'\]", str_val)
                    if match:
                        return match.group(1)
                    return str_val

                cleaned_series = df[actual_col].apply(clean_date)
                # Use default parsing with dayfirst=True to handle DD-MM-YYYY
                converted = pd.to_datetime(cleaned_series, errors='coerce', dayfirst=True)
                invalid = converted.isna() & cleaned_series.notna()
                error_indices[actual_col] = df.index[invalid].tolist()
                issues = np.where(invalid, "Invalid date format", "")
                index = 0
                while index < len(issues):
                    if issues[index]:
                        row_issues[index] = row_issues.get(index, []) + [issues[index]]
                    index += 1

            # NUMERIC: Check for numeric values, including pipe-separated phone numbers
            elif expected_type == "numeric":
                if expected_col == "Age":
                    def is_valid_age(value):
                        if pd.isna(value) or value == "":
                            return True
                        try:
                            num = float(str(value))
                            return num.is_integer() and isinstance(num, (int, float))
                        except (ValueError, TypeError):
                            return False
                    
                    invalid = df[actual_col].apply(lambda x: not is_valid_age(x))
                    error_indices[actual_col] = df.index[invalid].tolist()
                    issues = np.where(invalid, "Age must be a whole number", "")
                    index = 0
                    while index < len(issues):
                        if issues[index]:
                            row_issues[index] = row_issues.get(index, []) + [issues[index]]
                        index += 1
                else:
                    def is_numeric_list(value):
                        if pd.isna(value) or value == "":
                            return True
                        return all(part.strip().replace(r"[^\d]", "").isnumeric() for part in str(value).split("|"))
                    
                    invalid = df[actual_col].apply(lambda x: not is_numeric_list(x))
                    error_indices[actual_col] = df.index[invalid].tolist()
                    issues = np.where(invalid, "Non-numeric value in phone list", "")
                    index = 0
                    while index < len(issues):
                        if issues[index]:
                            row_issues[index] = row_issues.get(index, []) + [issues[index]]
                        index += 1

            # TEXT: Check for non-empty strings
            elif expected_type == "text":
                cleaned = df[actual_col].astype(str).str.strip()
                invalid = (cleaned == "") & (df[actual_col].notna())
                error_indices[actual_col] = df.index[invalid].tolist()
                issues = np.where(invalid, "Empty or whitespace text", "")
                index = 0
                while index < len(issues):
                    if issues[index]:
                        row_issues[index] = row_issues.get(index, []) + [issues[index]]
                    index += 1

            # EMAIL: Check for basic email format, including pipe-separated emails
            elif expected_type == "email":
                def is_valid_email_list(value):
                    if pd.isna(value) or value == "":
                        return True
                    emails = str(value).split("|")
                    return all(re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()) for email in emails)
                
                invalid = df[actual_col].apply(lambda x: not is_valid_email_list(x))
                error_indices[actual_col] = df.index[invalid].tolist()
                issues = np.where(invalid, "Invalid email format in list", "")
                index = 0
                while index < len(issues):
                    if issues[index]:
                        row_issues[index] = row_issues.get(index, []) + [issues[index]]
                    index += 1

    return error_indices, row_issues

if __name__ == "__main__":
    # Update expected_dtypes to include Age
    expected_dtypes = {
        "DOB": "date",
        "Phone": "numeric",
        "pan": "text",
        "DOD": "date",
        "Address": "text",
        "Email": "text",
        "Age": "numeric"
    }
    
    # Test data including Age
    data = {
        "DOB": ["['2000-05-12']", "['03-08-1968']", "['30-07-1927']", "[]", "invalid"],
        "Phone": ["9876543210", "9441924126|9701346831", "12345", "abcdefghij", "9999999999"],
        "pan": ["ABCDE1234X", "1234567890", "", "SHORT123", None],
        "DOD": ["2023-12-12", "invalid_date", None, "2010-06-10", "1999-01-01"],
        "Address": ["123 Street", "Apt", "    ", "Some Place", ""],
        "Email": ["user1@example.com", "arjunavalasasachivalayam@gmail.com|malleswararodalli1@gmail.com", "no@at", "user2@example.com", "test@domain.co"],
        "Age": [25, 30, "25.5", "abc", 45]  # Added Age column with various test cases
    }
    
    df = pd.DataFrame(data)
    matched_cols = {
        "DOB": "DOB",
        "Phone": "Phone",
        "pan": "pan",
        "DOD": "DOD",
        "Address": "Address",
        "Email": "Email",
        "Age": "Age"
    }
    
    error_indices, row_issues = dtype(df, expected_dtypes, matched_cols=matched_cols)
    print("\nData Type Error Indices:", error_indices)
    print("\nRow-wise Data Type Issues:", row_issues)