# main.py
import pandas as pd
from pathlib import Path
from Text_PreProc import preprocess_text, get_common_words, replace_words, normalize_pattern, load_excel, match_cols
from Pattern import pattern_clustering
from Logical import logical
from Excel_Handler import assign_colors, apply_colors_to_excel
from Data_Type import dtype
from Config import COLORS, PRIORITIES, EXPECTED_COLS, DTYPES
import time

def main(input_file_path: str, output_file_path: str) -> str:
    # Validate input file
    input_file = Path(input_file_path)
    if not input_file.exists() or not input_file.is_file() or input_file.suffix != '.xlsx':
        print(f"Error: '{input_file}' not found or is not a valid .xlsx file!")
        return None
    
    print(f"Processing file: {input_file}")
    output_file = Path(output_file_path)
    
    # Ensure the output directory exists
    output_file.parent.mkdir(exist_ok=True)
    
    # Load the Excel file
    df = load_excel(str(input_file))
    print(f" -- Loaded Excel file: {input_file}")
    
    # Create a copy for preprocessing
    df_preprocessed = df.copy()
    
    # Match columns to expected column names
    matched_cols = match_cols(df.columns, EXPECTED_COLS)
    print(f" ---- Matched columns: {matched_cols}")
    
    # Preprocess all columns for pattern validation
    text_cols = [col for col in df_preprocessed.columns]
    for col in text_cols:
        df_preprocessed = preprocess_text(df_preprocessed, col)
        common_words = get_common_words(df_preprocessed, col)
        df_preprocessed[col] = df_preprocessed[col].apply(
            lambda x: normalize_pattern(replace_words(str(x), common_words))
        )
    
    # Pattern discovery on all columns
    pattern_issues = {}
    pattern_row_issues = {}
    for col in df_preprocessed.columns:
        issues, updated_df, pattern_percentage_dict, row_issues = pattern_clustering(df_preprocessed, col, threshold=1.0)
        pattern_issues[col] = issues
        pattern_row_issues[col] = row_issues
        df_preprocessed[col] = updated_df[col]
    
    print("- Pattern Done")
    
    # Logical validation on matched columns
    logical_indices, logical_row_issues = logical(df, matched_cols=matched_cols)
    print("-- Logical Done")
    
    # Data type validation on matched columns
    dtype_indices, dtype_row_issues = dtype(df, DTYPES, matched_cols=matched_cols)
    print("--- Data Type Done")
    
    # Fill ratio calculation
    fill_ratios = {col: 1 - df[col].isna().mean() for col in df.columns}
    print("---- Fill Ratio Done")
    
    # Assign colors based on all issues
    cell_colors = assign_colors(logical_indices, pattern_issues, dtype_indices, COLORS, PRIORITIES)
    print("----- Colors Saved")
    
    # Apply colors to Excel, add Flag and Issues columns, and freeze them
    apply_colors_to_excel(input_file, cell_colors, fill_ratios, output_file, logical_row_issues, pattern_row_issues, dtype_row_issues)
    
    return str(output_file)

if __name__ == "__main__":
    from Config import Input_Folder, Output_Folder, Input_File
    start_time = time.time()
    input_file_path = Path(Input_Folder) / Input_File
    output_file_path = Path(Output_Folder) / f"{input_file_path.stem}_processed.xlsx"
    output_file = main(str(input_file_path), str(output_file_path))
    total = time.time() - start_time
    print(f"--- Processed in {total} seconds ---")
    if output_file:
        print(f"Output saved to: {output_file}")