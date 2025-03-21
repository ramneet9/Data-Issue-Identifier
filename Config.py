"""Configuration settings for colors, priorities, and expected columns."""

Input_Folder = "Input"
Output_Folder = "Output"

Input_File = "curated_data_for_testing_Preeti_Singh_19march2025.xlsx"


COLORS = {
    "logical": "ea697e",  # Red
    "pattern": "e1ea69",  # Yellow
    "dtype": "74ea69",    # Green
    "fill": "2596be"      # Blue 
}

PRIORITIES = {
    "logical": 3,  # Highest
    "pattern": 2,
    "dtype": 1     # Lowest
}

EXPECTED_COLS = {
    "DOB": ["Date of Birth", "Birth Date", "DOB"],
    "Phone": ["Phone", "Phone Number", "Mobile", "Contact"],
    "pan": ["PAN", "Pan Card", "pan", "PAN Number"],
    "DOD": ["Date of Death", "DOD", "Death Date"],
    "Address": ["Address", "Location", "Residence", "Home Address"],
    "Email": ["Email", "Email Address", "E-mail"],
    "Name": ["Name", "Full Name", "Person Name", "Customer Name"],
    # Additional expected columns
    "SSN": ["SSN", "Social Security Number", "Social Sec No"],
    "AccountNumber": ["Account Number", "Acct No", "Account ID"],
    "Gender": ["Gender", "Sex", "M/F"],
    "ZipCode": ["Zip Code", "Postal Code", "Zip"],
    "City": ["City", "Town", "Municipality"]
}

DTYPES = {
    "DOB": "date",
    "Phone": "numeric",
    "pan": "text",
    "DOD": "date",
    "Address": "text",
    "Email": "text",
    "Name": "text",
    # Data types for additional columns
    "SSN": "numeric",        # Assuming SSN is numeric (e.g., 123-45-6789 cleaned to 123456789)
    "AccountNumber": "text", # Could be alphanumeric
    "Gender": "text",        # M, F, Male, Female, etc.
    "ZipCode": "numeric",    # Typically 5 or 9 digits
    "City": "text"
}