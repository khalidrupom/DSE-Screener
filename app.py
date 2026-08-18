import streamlit as st
import pandas as pd
import numpy as np
from bdshare import get_current_trade_data

st.set_page_config(
    page_title="Live DSE Screener", 
    layout="wide", 
    page_icon="📈"
)

st.title("🔴 Live Dhaka Stock Exchange Screener")

# Load real-time live data from DSE with caching (refreshes every 5 minutes)
@st.cache_data(ttl=300)
def load_live_dse_data():
    try:
        df = get_current_trade_data()
        # Clean and map columns for technical analysis
        df = df.rename(columns={
            'symbol': 'Ticker',
            'ltp': 'Close_Price',
            'high': 'High',
            'low': 'Low',
            'volume': 'Volume_Today'
        })
        # Convert numeric columns safely
        for col in ['Close_Price', 'High', 'Low', 'Volume_Today', 'change']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching live data from DSE: {e}")
        return pd.DataFrame()

raw_df = load_live_dse_data()

if not raw_df.empty:
    st.success(f"Successfully connected live market data for {len(raw_df)} instruments from DSE.")
    
    # Simple ticker search filter
    search_term = st.text_input("Filter Ticker", "")
    if search_term:
        filtered_df = raw_df[raw_df['Ticker'].str.contains(search_term.upper(), na=False)]
    else:
        filtered_df = raw_df
        
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("Market might be closed or network connection is unavailable.")
