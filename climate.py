import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
import numpy as np
import io

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="🌍 Africa Climate Forecast", layout="wide", page_icon="☀️")

st.title("🌍 Africa Climate & Environmental Data Forecasting")
st.markdown("""
Analyze and forecast African climate trends based on historical environmental data.

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
# Data Processing
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
# Forecasting Section
# ----------------------------
st.subheader("🔮 Climate Variable Forecasting")

climate_vars = ['temperature', 'humidity', 'precipitation']
available_vars = [col for col in climate_vars if col in df.columns]

forecast_var = st.selectbox("Select variable to forecast", available_vars)
forecast_country = st.selectbox("Select country for forecast", sorted(df['country'].unique()))
future_year = st.slider("Select future year to forecast to", max_year + 1, max_year + 20, max_year + 5)

df_country = df[df['country'] == forecast_country].dropna(subset=[forecast_var])

# Prepare data for regression
df_train = df_country.groupby('year')[forecast_var].mean().reset_index()
X = df_train[['year']]
y = df_train[forecast_var]

model = LinearRegression()
model.fit(X, y)

# Predict into the future
years_future = np.arange(min_year, future_year + 1).reshape(-1, 1)
predictions = model.predict(years_future)

# Build forecast DataFrame
df_forecast = pd.DataFrame({
    'year': years_future.flatten(),
    f'forecast_{forecast_var}': predictions
})

st.line_chart(df_forecast.set_index('year'))

# ----------------------------
# Download Forecast Data
# ----------------------------
forecast_csv = df_forecast.to_csv(index=False)
st.download_button(
    label="📤 Download Forecasted Data",
    data=forecast_csv,
    file_name=f'forecast_{forecast_country}_{forecast_var}.csv',
    mime='text/csv'
)

# ----------------------------
# Footer
# ----------------------------
st.markdown("""
---
🛰️ Built with Streamlit, powered by historical data and simple forecasting. Customize this app to use more advanced models like Prophet, ARIMA, or LSTM for better results.
""")

