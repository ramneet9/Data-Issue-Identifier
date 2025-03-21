import pandas as pd
import numpy as np
from datetime import datetime
import re
from unidecode import unidecode

def is_invalid_name(name):
    if not isinstance(name, str):
        name = str(name)
    name = unidecode(name.strip()).lower()
    if not name or name == "nan":
        return ''
    if re.search(r"(.)\1{3,}", name):
        return "wrong: excessive repeated characters"
    if len(name) <= 2 and not re.search(r"[aeiouy]", name):
        return "wrong: too short and no vowels"
    if not re.search(r"[aeiouy]", name):
        return "wrong: no vowels"
    if re.search(r"[^aeiouy\s]{5,}", name):
        return "wrong: too many consecutive consonants"
    return "not wrong"

def logical_dob(dob_series, today):
    dob = pd.to_datetime(dob_series, errors='coerce')  # Relies on Data_Type.py for format validation
    conditions = [
        dob > today,
        (today.year - dob.dt.year) > 150
    ]
    choices = [
        "DOB is in the future",
        "DOB implies age > 150 years"
    ]
    mask = dob.notna()
    issues = pd.Series("", index=dob_series.index)
    if mask.any():
        issues[mask] = np.select(conditions, choices, default="")[mask]
    invalid = (issues != "") & (dob_series.notna())
    indices = dob_series.index[invalid].tolist()
    return indices, issues

def logical_phone(phone_series):
    def validate_phone_list(value):
        if pd.isna(value) or value == "":
            return ""
        phones = str(value).split("|")
        issues = []
        for phone in phones:
            cleaned = re.sub(r"[^\d]", "", phone.strip())
            if not re.match(r"^\d{10}$|^\d{12}$", cleaned):
                issues.append(f"Invalid phone: {phone}")
        return "; ".join(issues) if issues else ""

    issues = phone_series.apply(validate_phone_list)
    invalid = issues != ""
    indices = phone_series.index[invalid].tolist()
    return indices, issues

def logical_pan(pan_series):
    pan = pan_series.astype(str).str.strip()
    mask = pan_series.notna() & (pan != "")
    length_invalid = mask & (pan.str.len() != 10)
    length_indices = pan_series.index[length_invalid].tolist()
    length_issues = np.where(length_invalid, "PAN is not 10 characters", "")
    duplicates_mask = mask & pan.duplicated(keep=False)
    duplicate_indices = pan_series.index[duplicates_mask].tolist()
    duplicate_issues = np.where(duplicates_mask, "PAN is duplicated", "")
    issues = pd.Series("", index=pan_series.index)
    for idx, (length_issue, dup_issue) in zip(pan_series.index, zip(length_issues, duplicate_issues)):
        if length_issue or dup_issue:
            issues[idx] = "; ".join([i for i in [length_issue, dup_issue] if i])
    return length_indices, duplicate_indices, issues

def logical_age(age_series, today):
    age = pd.to_numeric(age_series, errors='coerce')
    conditions = [
        age < 0,
        age > 140
    ]
    choices = [
        "Age cannot be less than 0",
        "Age cannot be more than 140"
    ]
    mask = age.notna()
    issues = pd.Series("", index=age_series.index)
    if mask.any():
        issues[mask] = np.select(conditions, choices, default="")[mask]
    invalid = (issues != "") & (age_series.notna())
    indices = age_series.index[invalid].tolist()
    return indices, issues

def logical_dod(dod_series, today):
    dod = pd.to_datetime(dod_series, errors='coerce')
    invalid = dod.notna() & (dod > today)
    issues = np.where(invalid, "DOD is in the future", "")
    indices = dod_series.index[invalid].tolist()
    return indices, pd.Series(issues, index=dod_series.index)

def logical_address(address_series):
    addr = address_series.astype(str).str.strip()
    mask = address_series.notna() & (addr != "")
    invalid = mask & (addr.str.len() <= 5)
    issues = np.where(invalid, "Address is too short (≤ 5 characters)", "")
    indices = address_series.index[invalid].tolist()
    return indices, pd.Series(issues, index=address_series.index)

def logical_email(email_series):
    def validate_email_list(value):
        if pd.isna(value) or value == "":
            return ""
        emails = str(value).split("|")
        issues = []
        for email in emails:
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()):
                issues.append(f"Invalid email: {email}")
        return "; ".join(issues) if issues else ""

    issues = email_series.apply(validate_email_list)
    invalid = issues != ""
    indices = email_series.index[invalid].tolist()
    return indices, issues

def logical_name(name_series):
    mask = name_series.notna() & (name_series.astype(str) != "")
    issues = pd.Series("", index=name_series.index)
    if mask.any():
        issues[mask] = name_series[mask].apply(is_invalid_name).replace("not wrong", "")
    invalid = issues != ""
    indices = name_series.index[invalid].tolist()
    return indices, issues

def logical(df, matched_cols=None):
    today = pd.Timestamp(datetime.today().date())
    error_indices = {col: [] for col in matched_cols.values()} if matched_cols else {}
    error_indices["Duplicates"] = []
    row_issues = {}

    col_funcs = {
        "DOB": lambda col: logical_dob(df[col], today),
        "Phone": lambda col: logical_phone(df[col]),
        "pan": lambda col: logical_pan(df[col]),
        "DOD": lambda col: logical_dod(df[col], today),
        "Address": lambda col: logical_address(df[col]),
        "Email": lambda col: logical_email(df[col]),
        "Name": lambda col: logical_name(df[col]),
        "Age": lambda col: logical_age(df[col], today)
    }

    if matched_cols:
        for expected_col, actual_col in matched_cols.items():
            if expected_col in col_funcs:
                if expected_col == "pan":
                    length_indices, duplicate_indices, issues = col_funcs[expected_col](actual_col)
                    error_indices[actual_col] = length_indices
                    error_indices["Duplicates"] = duplicate_indices
                else:
                    indices, issues = col_funcs[expected_col](actual_col)
                    error_indices[actual_col] = indices
                for idx, issue in issues.items():
                    if issue:
                        issue_list = issue.split("; ") if "; " in issue else [issue]
                        row_issues[idx] = row_issues.get(idx, []) + issue_list

    return error_indices, row_issues

if __name__ == "__main__":
    data = {
        "DOB": ["2000-05-12", "03-08-1968", "2050-12-01", None, "1998-07-15"],
        "Phone": ["9876543210", "9441924126|9701346831", "12345", "abc|9441924126", ""],
        "pan": ["ABCDE1234X", "1234567890", "ABCDE1234X", "SHORT123", None],
        "DOD": ["2023-12-12", "2050-01-01", None, "2010-06-10", ""],
        "Address": ["123 Street", "Apt", "    ", "Some Place", ""],
        "Email": ["user1@example.com", "arjunavalasasachivalayam@gmail.com|malleswararodalli1@gmail.com|sachivalayamkrishnapuram@gmail.com", "no@at", "abc@|xyz@gmail.com", ""],
        "Name": ["John", "Effff", "Xy", "", "Alice"]
    }
    df = pd.DataFrame(data)
    matched_cols = {
        "DOB": "DOB",
        "Phone": "Phone",
        "pan": "pan",
        "DOD": "DOD",
        "Address": "Address",
        "Email": "Email",
        "Name": "Name",
        "Age": "Age"
    }
    error_indices, row_issues = logical(df, matched_cols=matched_cols)
    print("error_indices:", error_indices)
    print("\nrow_issues:", row_issues)