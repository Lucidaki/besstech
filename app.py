import streamlit as st
import pandas as pd
from data import get_bess_data

# Page Configuration
st.set_page_config(
    page_title="BESS Technology Dashboard",
    page_icon="🔋",
    layout="wide"
)

# Title and Introduction
st.title("🔋 BESS Technology Dashboard: Performance & Finance Outlook")
st.markdown("""
This dashboard provides a comparative analysis of Battery Energy Storage System (BESS) technologies.
It explores the current landscape and projects future trends over 3, 5, and 10-year horizons.
""")

# Load Data
@st.cache_data
def load_data():
    return get_bess_data()

try:
    df = load_data()
    st.success(f"Data successfully loaded! ({len(df)} records)")
    
    # Quick Preview (Hidden in Expander)
    with st.expander("View Raw Data"):
        st.dataframe(df)
        
except Exception as e:
    st.error(f"Error loading data: {e}")

# Sidebar
st.sidebar.header("Configuration")
st.sidebar.info("Select options to filter charts (Coming Soon)")
