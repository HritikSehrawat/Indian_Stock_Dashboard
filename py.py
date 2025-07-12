import streamlit as st
import yfinance as yf
import pandas as pd


st.set_page_config(page_title="Indian Stock Dashboard")
st.header("Indian Stock Dashboard")


# Load NSE and BSE symbol data
nse_df = pd.read_csv("nse_symbols.csv")  
bse_df = pd.read_csv("bse_symbols.csv")  

# Sidebar exchange selection
exchange = st.selectbox("Exchange", ["NSE", "BSE"], index=0)

# Pick the right dataframe
stock_df = nse_df if exchange == "NSE" else bse_df

# Create selectbox options like "INFY - Infosys Ltd"
stock_options = stock_df.apply(lambda row: f"{row['Symbol']} - {row['Name']}", axis=1)

# Symbol selection from dropdown
selected_option = st.selectbox("Select Stock", stock_options)

# Extract actual symbol
symbol_input = selected_option.split(" - ")[0]

# Append correct suffix
suffix = ".NS" if exchange == "NSE" else ".BO"
ticker_symbol = f"{symbol_input}{suffix}"


# Create full ticker symbol with suffix
suffix = ".NS" if exchange == "NSE" else ".BO"
ticker_symbol = f"{symbol_input.upper().split('.')[0]}{suffix}"

# Format helper
def safe_format(val):
    try:
        if isinstance(val, (int, float)):
            return f"{val:,.2f}"
        return str(val)
    except:
        return str(val)

# Function to fetch stock data
@st.cache_data(show_spinner=False)
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d')

        if hist.empty:
            return None

        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        high_price = hist['High'].iloc[-1]
        low_price = hist['Low'].iloc[-1]
        info = stock.info

        return {
            'Price': float(current_price),
            'Previous Close': float(previous_close),
            'Day High': float(high_price),
            'Day Low': float(low_price),
            'Change (%)': ((current_price - previous_close) / previous_close * 100) if previous_close else 0,
            'Market Cap': info.get('marketCap', 'N/A'),
            'About': info.get('longBusinessSummary', 'Not available')[:500] + "..." if info.get('longBusinessSummary') else "Not available",
            'Sector': info.get('sector', 'N/A'),
            'PE Ratio': info.get('trailingPE', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A')
        }

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Main display logic
if st.button("Get Data"):
    st.subheader(f"📊 {ticker_symbol} Stock Data")

    data = get_stock_data(ticker_symbol)

    if data:
        # Display key stats
        st.markdown("### 🔢 Key Stock Info")
        display_data = {
            'Price': data['Price'],
            'Previous Close': data['Previous Close'],
            'Day High': data['Day High'],
            'Day Low': data['Day Low'],
            'Change (%)': data['Change (%)'],
            'Market Cap': data['Market Cap']
        }
        df = pd.DataFrame.from_dict(display_data, orient='index', columns=['Value'])
        st.dataframe(df.style.format({'Value': safe_format}))

        # Company Description
        st.markdown("### 🏢 Company Overview")
        st.info(data['About'])

        # Key Metrics
        st.markdown("### 📌 Key Metrics")
        metrics = {
            'Sector': data['Sector'],
            'PE Ratio': data['PE Ratio'],
            '52 Week High': data['52 Week High'],
            '52 Week Low': data['52 Week Low']
        }
        metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
        st.table(metrics_df.style.format({'Value': safe_format}))
    else:
        st.warning("No data found. Please check the symbol or try a different one.")
else:
    st.info("Enter a stock symbol and click **Get Data** to view information.")


# Optional styling
st.markdown("""
<style>
    .stDataFrame {
        width: 100%;
    }
    .stTable {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)
