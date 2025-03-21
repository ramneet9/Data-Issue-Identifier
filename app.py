import streamlit as st
import pandas as pd
from pathlib import Path
import time
from main import main
import os

st.set_page_config(page_title="Data Issue Identifier", page_icon="📊", layout="wide")

# Initialize session state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "processed_file_path" not in st.session_state:
    st.session_state.processed_file_path = None
if "processing_time" not in st.session_state:
    st.session_state.processing_time = None
if "show_toast" not in st.session_state:
    st.session_state.show_toast = False
if "toast_timer" not in st.session_state:
    st.session_state.toast_timer = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = "file_uploader_0"  # Initial key for file uploader

def toggle_dark_mode():
    if not st.session_state.file_uploaded:
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    else:
        # Show toast for 2 seconds
        st.session_state.show_toast = True
        st.session_state.toast_timer = time.time()

def reset_app():
    # Preserve dark_mode state, reset everything else
    current_dark_mode = st.session_state.dark_mode
    current_key = st.session_state.uploader_key
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Restore dark_mode and set a new uploader key
    st.session_state.dark_mode = current_dark_mode
    st.session_state.uploader_key = f"file_uploader_{int(current_key.split('_')[-1]) + 1}"
    st.rerun()

# Apply CSS based on dark mode state
st.markdown(
    """
    <style>
    .stApp {
        background-color: %s;
        color: %s;
    }
    .stButton>button {
        background-color: #4CAF50;  /* Green for Process button */
        color: white;
        border-radius: 10px;
        font-size: 16px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #000000;  /* Black on hover */
        color: white;
    }
    .stFileUploader label, 
    .stFileUploader div[role="button"] span, 
    .stFileUploader div[data-testid="fileUploadDropzone"] span,
    .stFileUploader div[data-testid="stFileUploaderFileName"],
    .stFileUploader div[data-testid="stFileUploadedStatus"] span {
        color: %s !important;  /* Targets "Drag and drop file here", file name, and size text */
    }
    .toggle-btn {
        position: absolute;
        top: 15px;
        right: 40px;  /* Moved further right for better alignment */
    }
    .stDownloadButton>button {
        background-color: #2196F3;  /* Blue for Download button */
        color: %s;
        border-radius: 10px;
        transition: background-color 0.3s;
    }
    .stDownloadButton>button:hover {
        background-color: #000000;  /* Black on hover */
        color: white;
    }
    span:not(.stFileUploader span) {
        color: %s !important;
    }
    .toast {
        position: fixed;
        top: 60px;
        right: 20px;
        background-color: #ff4444;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        z-index: 1000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .home-btn {
        position: absolute;
        top: 15px;
        left: 20px;
    }
    </style>
    """ % (
        "#1E1E1E" if st.session_state.dark_mode else "#FFFFFF",
        "#FFFFFF" if st.session_state.dark_mode else "#000000",
        "#FFFFFF" if st.session_state.dark_mode else "#333333",  # White in dark, dark gray in light
        "white" if st.session_state.dark_mode else "black",
        "#FFFFFF" if st.session_state.dark_mode else "#000000"
    ),
    unsafe_allow_html=True,
)

# Layout with Home and toggle buttons
col1, col2, col3, col4 = st.columns([1, 6, 1, 1])  # Added a fourth column
with col1:
    if st.button("🏠", key="home_button"):
        reset_app()
with col4:
    if st.button("🌙", key="dark_mode_toggle"):
        toggle_dark_mode()

# Toast notification
if st.session_state.show_toast:
    st.markdown(
        '<div class="toast">Mode can only be changed before uploading a file.</div>',
        unsafe_allow_html=True
    )
    # Check if 2 seconds have passed
    if st.session_state.toast_timer and (time.time() - st.session_state.toast_timer >= 2):
        st.session_state.show_toast = False
        st.session_state.toast_timer = None

st.title("📊 Data Issue Identifier")
st.write('<span>Please upload your Excel file and click \'Process\' to analyze it.</span>', 
         unsafe_allow_html=True)

# File uploader with dynamic key
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key=st.session_state.uploader_key)

# Process file
if uploaded_file is not None:
    st.session_state.file_uploaded = True
    # Create temporary directory
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    input_file_path = temp_dir / uploaded_file.name
    output_file_path = temp_dir / f"{Path(uploaded_file.name).stem}_processed.xlsx"
    
    # Save uploaded file to temp directory
    with open(input_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write('<span>File uploaded successfully!</span>', unsafe_allow_html=True)
    
    # Process button
    if st.session_state.processed_file_path is None and st.button("Process", key="process_button"):
        st.write('<span>Processing the file...</span>', unsafe_allow_html=True)
        start_time = time.time()
        
        # Call main() with both input and output file paths
        processed_file = main(str(input_file_path), str(output_file_path))
        total_time = time.time() - start_time
        
        if processed_file and Path(processed_file).exists():
            st.session_state.processed_file_path = processed_file
            st.session_state.processing_time = total_time
            # Clean up input file immediately
            os.remove(input_file_path)
        else:
            st.error("Processed file not found. Please check the processing logic.")

# Display download button if processing is complete
if st.session_state.processed_file_path is not None and Path(st.session_state.processed_file_path).exists():
    st.write(f'<span>Processing completed in {st.session_state.processing_time:.2f} seconds.</span>', 
             unsafe_allow_html=True)
    with open(st.session_state.processed_file_path, "rb") as f:
        st.download_button(
            label="Download Processed File",
            data=f,
            file_name=Path(st.session_state.processed_file_path).name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button"
        )
else:
    if not uploaded_file:
        st.session_state.file_uploaded = False
        st.session_state.processed_file_path = None
        st.session_state.processing_time = None
        st.write('<span>Please upload an Excel file to get started.</span>', 
                 unsafe_allow_html=True)