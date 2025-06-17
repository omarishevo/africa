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
# File Upload
# ----------------------------
uploaded_file = st.file_uploader("📤 Upload CSV File with Climate Data", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to read uploaded CSV: {e}")
        st.stop()
else:
    st.warning("⚠️ Please upload a CSV file to proceed.")
    st.stop()

# ----------------------------
# Flexible Date Column Handling
# ----------------------------
possible_date_cols = ['date', 'recorded_date', 'observation_date', 'year_month']
date_col_found = None

for col in df.columns:
    if col.lower().strip() in possible_date_cols:
        date_col_found = col
        break

if not date_col_found:
    st.error("❌ Dataset must include a date-related column like 'date', 'recorded_date', or 'observation_date'.")
    st.stop()

df.rename(columns={date_col_found: 'date'}, inplace=True)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year
df.dropna(subset=['date', 'year'], inplace=True)

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("🔎 Filter Data")
countries = df['country'].dropna().unique()
selected_countries = st.sidebar.multiselect("Select Countries", sorted(countries), default=list(countries[:3]))

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
# Forecasting (No ML Library)
# ----------------------------
st.subheader("🔮 Climate Forecasting (using NumPy)")

climate_vars = ['temperature', 'humidity', 'precipitation']
available_vars = [col]()_
