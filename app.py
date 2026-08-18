import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="DSE Screener", layout="wide")
st.title("📊 DSE Funnel Screener")

# Mock data generation
@st.cache_data
def get_data():
    tickers = [f"STOCK_{i}" for i in range(1, 51)]
    return pd.DataFrame({
        'Ticker': tickers,
        'PE_Ratio': np.random.uniform(5, 30, 50),
        'Price': np.random.uniform(10, 500, 50)
    })

df = get_data()

st.sidebar.header("Filters")
max_pe = st.sidebar.slider("Max P/E", 5, 30, 20)
filtered_df = df[df['PE_Ratio'] <= max_pe]

st.dataframe(filtered_df, use_container_width=True)
