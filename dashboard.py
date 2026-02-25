import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set up the Streamlit app configuration
st.set_page_config(page_title="Bitcoin Rolling Correlation", layout="wide")
st.title("📈 Bitcoin Rolling Correlation Dashboard")

# Mapping of human‑readable asset names to their Yahoo Finance tickers
TICKERS = {
    "Bitcoin": "BTC-USD",
    "Gold": "GC=F",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "SET50": "^N225",
}

# Mapping of time period labels to yfinance period strings
# Added 3 Years and 5 Years timeframes per user request
PERIODS = {
    "30 Days": "1mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "3 Years": "3y",
    "5 Years": "5y",
    "10 Years": "10y",
    "All Time": "max",
}

# Sidebar configuration
st.sidebar.header("⚙️ การตั้งค่ากราฟ")

# Allow the user to select which assets to compare against Bitcoin
selected_assets = st.sidebar.multiselect(
    "เลือกสินทรัพย์เทียบกับ Bitcoin:",
    options=[k for k in TICKERS.keys() if k != "Bitcoin"],
    default=["Gold", "NASDAQ"],
)

# Allow the user to select a time period
selected_period = st.sidebar.selectbox(
    "เลือกช่วงเวลา:",
    options=list(PERIODS.keys()),
    index=2,  # Default to "1 Year"
)

# Slider for rolling window size in days
rolling_window = st.sidebar.slider(
    "Rolling Window (จำนวนวันสำหรับการคำนวณ Correlation ในแต่ละจุด):",
    min_value=7,
    max_value=90,
    value=30,
    step=1,
)

# Cache the data loading function to avoid redundant API calls
@st.cache_data(ttl=3600)
def load_data(assets, period_key):
    """Load historical price data for Bitcoin and selected assets.

    Parameters
    ----------
    assets : list of str
        List of asset names to load (excluding Bitcoin). Bitcoin is always included.
    period_key : str
        Key from the PERIODS dict specifying the desired time range.

    Returns
    -------
    pct_return_df : pandas.DataFrame
        Percentage returns from the start of the period, indexed by date.
    close_df : pandas.DataFrame
        Raw closing prices for each asset, indexed by date.
    """
    # Always include Bitcoin
    assets_to_load = ["Bitcoin"] + assets
    period_val = PERIODS[period_key]
    tickers_list = [TICKERS[a] for a in assets_to_load]

    # Download price data from Yahoo Finance
    df = yf.download(tickers_list, period=period_val)

    # Handle the case where yfinance returns a different DataFrame format when only one ticker is fetched
    if len(tickers_list) == 1:
        close_df = df[["Close"]].copy()
        close_df.columns = [tickers_list[0]]
    else:
        close_df = df["Close"].copy()

    # Rename the columns back to human‑readable asset names
    reverse_map = {v: k for k, v in TICKERS.items()}
    close_df = close_df.rename(columns=reverse_map)

    # Forward fill missing values and drop any remaining NaNs
    close_df = close_df.ffill().dropna()

    # Compute percentage returns relative to the first available price
    pct_return_df = ((close_df / close_df.iloc[0]) - 1) * 100

    return pct_return_df, close_df

# If the user has selected at least one asset, proceed to load and display data
if selected_assets:
    pct_df, raw_df = load_data(selected_assets, selected_period)

    # Plot percentage returns comparison
    fig_price = px.line(
        pct_df,
        title=f"Percentage Return Comparison ({selected_period})",
        labels={"value": "Return (%)", "Date": "Date", "variable": "Asset"},
        template="plotly_dark",
    )
    fig_price.update_layout(hovermode="x unified")
    st.plotly_chart(fig_price, use_container_width=True)

    # Rolling correlation section
    st.subheader(f"🔗 {rolling_window}-Day Rolling Pearson Correlation with Bitcoin")
    st.markdown("แสดงการเปลี่ยนแปลงของความสัมพันธ์เมื่อเวลาผ่านไป (Y-Axis ล็อคที่ -1 ถึง 1)")

    # Daily returns for correlation calculations
    daily_returns = raw_df.pct_change().dropna()

    # Prepare a DataFrame to hold rolling correlations
    rolling_corr_df = pd.DataFrame(index=daily_returns.index)

    for asset in selected_assets:
        rolling_corr_df[asset] = daily_returns[asset].rolling(window=rolling_window).corr(daily_returns["Bitcoin"])

    rolling_corr_df = rolling_corr_df.dropna()

    if not rolling_corr_df.empty:
        fig_corr = go.Figure()

        for asset in selected_assets:
            fig_corr.add_trace(
                go.Scatter(
                    x=rolling_corr_df.index,
                    y=rolling_corr_df[asset],
                    mode="lines",
                    name=asset,
                )
            )

        fig_corr.update_layout(
            template="plotly_dark",
            title=f"Rolling Correlation vs Bitcoin (Window={rolling_window} days)",
            xaxis_title="Date",
            yaxis_title="Correlation (-1 to 1)",
            yaxis=dict(range=[-1.1, 1.1]),
            hovermode="x unified",
        )

        # Add a horizontal line at zero correlation for reference
        fig_corr.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)

        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info(
            f"ข้อมูลไม่เพียงพอสำหรับการคำนวณ Rolling Correlation (ต้องการข้อมูลมากกว่า {rolling_window} วัน) โปรดเลือกช่วงเวลาที่ยาวขึ้น"
        )
else:
    st.warning(
        "👈 กรุณาเลือกสินทรัพย์อย่างน้อย 1 รายการจากเมนูด้านซ้ายเพื่อเปรียบเทียบกับ Bitcoin"
    )