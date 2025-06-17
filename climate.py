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
available_vars = [col for col in climate_vars if col in df.columns]

if not available_vars:
    st.warning("⚠️ No forecastable variables ('temperature', 'humidity', 'precipitation') found in dataset.")
    st.stop()

forecast_var = st.selectbox("Select variable to forecast", available_vars)
forecast_country = st.selectbox("Select country for forecast", sorted(df['country'].unique()))
future_year = st.slider("Select future year to forecast to", max_year + 1, max_year + 20, max_year + 5)

df_country = df[df['country'] == forecast_country].dropna(subset=[forecast_var])
df_train = df_country.groupby('year')[forecast_var].mean().reset_index()

years = df_train['year'].values
values = df_train[forecast_var].values

if len(years) >= 2:
    coeffs = np.polyfit(years, values, 1)  # Linear regression: y = mx + b
    m, b = coeffs

    future_years = np.arange(min(years), future_year + 1)
    future_preds = m * future_years + b

    df_forecast = pd.DataFrame({
        'year': future_years,
        f'forecast_{forecast_var}': future_preds
    })

    st.line_chart(df_forecast.set_index('year'))

    forecast_csv = df_forecast.to_csv(index=False)
    st.download_button(
        label="📤 Download Forecasted Data",
        data=forecast_csv,
        file_name=f'forecast_{forecast_country}_{forecast_var}.csv',
        mime='text/csv'
    )
else:
    st.warning("⚠️ Not enough data points for forecasting.")

# ----------------------------
# Footer
# ----------------------------
st.markdown("""
---
🛰️ Built with Streamlit and NumPy. For more accurate forecasting, consider using libraries like `Prophet` or `statsmodels`.
""")
