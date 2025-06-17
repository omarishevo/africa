import pandas as pd
import streamlit as st
import numpy as np

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="🌍 Africa Climate Forecast", layout="wide", page_icon="☀️")

st.title("🌍 Africa Climate & Environmental Data Forecasting (No ML Library)")
st.markdown("""
Analyze and forecast African climate trends using historical data.

Forecasting is based on simple linear estimation using NumPy.

---
""")

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("africa_climate_environmental_data_5000.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# ----------------------------
# Data Preprocessing
# ----------------------------
if 'date' not in df.columns:
    st.error("Dataset must include a 'date' column.")
    st.stop()

df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year
df.dropna(subset=['date', 'year'], inplace=True)

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("🔎 Filter Data")
countries = df['country'].dropna().unique()
selected_countries = st.sidebar.multiselect("Select Countries", sorted(countries), default=["Kenya"])

min_year = int(df['year'].min())
max_year = int(df['year'].max())
year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1])
]

# ----------------------------
# Summary Statistics
# ----------------------------
st.subheader("📊 Summary Statistics")
with st.expander("Show Summary Table"):
    st.write(df_filtered.describe(include='all'))

# ----------------------------
# Download Filtered Data
# ----------------------------
st.subheader("⬇️ Download Filtered Data")
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered CSV",
    data=csv,
    file_name='filtered_climate_data.csv',
    mime='text/csv'
)

# ----------------------------
# Forecasting (No scikit-lear
