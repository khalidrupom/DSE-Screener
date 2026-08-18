import streamlit as st
import pandas as pd
import datetime as dt
from bdshare import get_historical_data

st.set_page_config(page_title="DSE 10-Year Historical Data", layout="wide")

st.title("📊 DSE 10-Year Historical Data Archive")
st.markdown("Fetch, analyze, and download a decade of price history for Dhaka Stock Exchange equities.")

# Input controls for historical range
ticker_symbol = st.text_input("Enter DSE Ticker Symbol (e.g., KPPL, SQURPHARMA):", "KPPL").upper()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", dt.date.today() - dt.timedelta(days=365*10))
with col2:
    end_date = st.date_input("End Date", dt.date.today())

if st.button("Fetch 10-Year History"):
    with st.spinner(f"Crawling 10-year records for {ticker_symbol} from DSE..."):
        try:
            # Fetch historical data using bdshare
            df_history = get_historical_data(str(start_date), str(end_date), ticker_symbol)
            
            if df_history is not None and not df_history.empty:
                st.success(f"Successfully loaded {len(df_history)} trading sessions for {ticker_symbol}!")
                
                # Display metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Records", len(df_history))
                m2.metric("Starting Price", f"{df_history['close'].iloc[-1]:.2f} BDT")
                m3.metric("Latest Price", f"{df_history['close'].iloc[0]:.2f} BDT")
                
                # Show Data Table
                st.subheader("Historical Price Table (OHLCV)")
                st.dataframe(df_history, use_container_width=True)
                
                # Download CSV button for mobile backup
                csv_data = df_history.to_csv().encode('utf-8')
                st.download_button(
                    label=f"📥 Download {ticker_symbol} 10-Year CSV",
                    data=csv_data,
                    file_name=f"{ticker_symbol}_10yr_history.csv",
                    mime="text/csv",
                )
            else:
                st.warning(f"No historical records found for ticker '{ticker_symbol}' within the selected timeline. Check the spelling or try another symbol.")
        except Exception as e:
            st.error(f"Error fetching historical timeline: {e}")
