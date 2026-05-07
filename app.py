import streamlit as st

st.set_page_config(page_title="AI Stock System", layout="wide")

# Hide sidebar until login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display: none;}
        header {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    from login import login_page
    login_page()
    st.stop()

from data_fetcher import fetch_stock
from indicators import add_indicators
from prophet_model import prophet_forecast
from evaluation import rmse
from history import save_history, get_history
from news_sentiment import get_sentiment
from signals import trading_signal
import plotly.graph_objects as go
import numpy as np

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] * {
        color: #cbd5f5 !important;
        font-size: 14px;
    }

    div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
        background-color: #2563eb;
        color: white !important;
        border-radius: 6px;
    }

    .block-container {
        padding-top: 1.5rem;
    }

    h1 {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #f8fafc;
    }

    h2, h3 {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

user = st.session_state.user
st.title("AI Stock Forecasting Platform")
st.caption("AI-Based Stock Market Forecasting System")

st.sidebar.markdown("### Navigation")
menu = st.sidebar.radio(
    "",
    ["Dashboard", "Prediction", "History", "News Sentiment", "Model Compare"]
)

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.header("Stock Analysis Dashboard")

    ticker = st.text_input("Stock Symbol (AAPL, TSLA, RELIANCE.NS)")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", key="dash_start")
    with col2:
        end_date = st.date_input("End Date", key="dash_end")

    if ticker == "":
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be less than end date")
        st.stop()

    df = fetch_stock(ticker, str(start_date), str(end_date))
    df.dropna(inplace=True)

    if df.empty or len(df) < 2:
        st.error("Not enough data")
        st.stop()

    df = add_indicators(df)

    latest = float(df["Close"].iloc[-1])
    prev = float(df["Close"].iloc[-2])
    change = latest - prev
    percent = (change / prev) * 100 if prev != 0 else 0

    rsi = float(df["RSI"].iloc[-1])
    signal = trading_signal(rsi)

    m1, m2, m3 = st.columns(3)
    m1.metric("Price", f"{latest:.2f}", f"{change:.2f} ({percent:.2f}%)")
    m2.metric("RSI", f"{rsi:.2f}")
    m3.metric("Signal", signal)

    st.divider()

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing=dict(line=dict(color="green")),
            decreasing=dict(line=dict(color="red")),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["SMA_20"],
            name="SMA",
            line=dict(color="orange"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["EMA_20"],
            name="EMA",
            line=dict(color="blue"),
        )
    )

    fig.update_layout(template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

    rsi_fig = go.Figure()
    rsi_fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["RSI"],
            name="RSI",
            line=dict(color="purple"),
        )
    )
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(rsi_fig, use_container_width=True)

# ================= PREDICTION =================
elif menu == "Prediction":
    st.header("Prediction")

    ticker = st.text_input("Stock", key="pred_ticker")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", key="pred_start")
    with col2:
        end_date = st.date_input("End Date", key="pred_end")

    if ticker == "":
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be less than end date")
        st.stop()

    df = fetch_stock(ticker, str(start_date), str(end_date))
    df.dropna(inplace=True)

    if df.empty:
        st.error("No data available")
        st.stop()

    df = add_indicators(df)
    days = st.slider("Forecast Days", 1, 365, 30)

    if st.button("Run Prophet"):
        forecast = prophet_forecast(df, days)
        pred = float(forecast["yhat"].iloc[-1])

        st.success(f"Predicted Price: {pred:.2f}")
        save_history(user, ticker, pred)

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df["Close"],
                name="Actual",
                line=dict(color="green"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=forecast["ds"],
                y=forecast["yhat"],
                name="Prediction",
                line=dict(color="cyan", dash="dash"),
            )
        )

        fig.update_layout(template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Forecast Data")
        st.dataframe(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(10))

# ================= HISTORY =================
elif menu == "History":
    st.header("History")
    data = get_history(user)
    st.dataframe(data)
    st.download_button(
        "Download CSV",
        data.to_csv(index=False),
        file_name="history.csv",
    )

# ================= NEWS =================
elif menu == "News Sentiment":
    st.header("News Sentiment")

    ticker = st.text_input("Stock", key="news_ticker")

    if ticker == "":
        st.stop()

    sentiment = get_sentiment(ticker)
    st.subheader(f"Sentiment: {sentiment}")

    if sentiment == "Positive":
        st.success("Stock may go UP")
    elif sentiment == "Negative":
        st.error("Stock may go DOWN")
    else:
        st.warning("Neutral")

# ================= MODEL COMPARE =================
elif menu == "Model Compare":
    st.header("Model Comparison")

    ticker = st.text_input("Stock", key="comp_ticker")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", key="comp_start")
    with col2:
        end_date = st.date_input("End Date", key="comp_end")

    if ticker == "":
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be less than end date")
        st.stop()

    df = fetch_stock(ticker, str(start_date), str(end_date))
    df.dropna(inplace=True)

    if len(df) < 100:
        st.error("Need more data")
        st.stop()

    if st.button("Compare"):
        split = int(len(df) * 0.8)
        train = df[:split]
        test = df[split:]

        forecast = prophet_forecast(train, len(test))
        y_pred = forecast["yhat"].tail(len(test)).values
        y_true = test["Close"].values
        prophet_rmse = rmse(y_true, y_pred)

        df["MA"] = df["Close"].rolling(5).mean()
        ma_rmse = rmse(df["Close"][5:], df["MA"][5:])

        st.write("Prophet RMSE:", round(prophet_rmse, 2))
        st.write("MA RMSE:", round(ma_rmse, 2))

        if prophet_rmse < ma_rmse:
            st.success("Best Model: Prophet")
        else:
            st.success("Best Model: Moving Average")
