# ==========================================
# CPR + Breakout Strategy - Streamlit App
# ==========================================
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="CPR + Breakout Strategy", layout="wide")

st.title("📊 CPR-Breakout Strategy")

# --------------------------
# User Inputs

# todays data CPR

# Upload Nifty200 stock list
uploaded_file = st.file_uploader("Upload your stock list CSV (with 'Symbol' column)", type=["csv"])

if uploaded_file is not None:
    stocks_df = pd.read_csv(uploaded_file)
    stocks = stocks_df["Symbol"].tolist()

    today = datetime.today().date()
    qualified_stocks = []

    progress_bar = st.progress(0)
    total = len(stocks)

    for idx, ticker in enumerate(stocks):
        try:
            # ---- Step 1: Daily data (15 days) ----
            daily = yf.download(ticker, period="15d", interval="1d")

            if len(daily) < 3:
                continue

            # Yesterday OHLC (for CPR)
            yday_high = float(daily["High"].iloc[-2])
            yday_low = float(daily["Low"].iloc[-2])
            yday_close = float(daily["Close"].iloc[-2])

            # Today reference OHLC
            today_high = float(daily["High"].iloc[-1])
            today_low = float(daily["Low"].iloc[-1])
            today_close = float(daily["Close"].iloc[-1])

            # CPR for yesterday
            y_pivot = (yday_high + yday_low + yday_close) / 3
            y_bc = (yday_high + yday_low) / 2
            y_tc = 2 * y_pivot - y_bc

            # CPR for today
            t_pivot = (today_high + today_low + today_close) / 3
            t_bc = (today_high + today_low) / 2
            t_tc = 2 * t_pivot - t_bc

            # Ascending CPR check
            if not (t_pivot > y_pivot and t_bc > y_bc and t_tc > y_tc):
                continue

            # ---- Step 2: Intraday 5-min data ----
            intraday = yf.download(
                ticker,
                start=daily.index[-1].date(),
                end=daily.index[-1].date() + timedelta(days=1),
                interval="5m"
            ).reset_index()

            if intraday.empty:
                continue

            # First 5-min candle
            # first_candle = intraday.iloc[0]
            # first_close = float(first_candle["Close"])

             #First 5-min candle
            first_candle = intraday.iloc[0]
            first_open = float(first_candle["Open"])
            first_close = float(first_candle["Close"])

            # Check condition
            if (first_close > first_open) and (first_close > yday_high):
                qualified_stocks.append(ticker)

        except Exception as e:
            st.warning(f"⚠️ Error processing {ticker}: {e}")
            continue

        progress_bar.progress((idx + 1) / total)

    # --------------------------
    # Step 3: Results
    # --------------------------
    if qualified_stocks:
        st.success("✅ Stocks satisfying conditions:")
        result_df = pd.DataFrame(qualified_stocks, columns=["Qualified Stocks"])
        st.dataframe(result_df)

        # Save to CSV
        csv_file = "qualified_stocks.csv"
        result_df.to_csv(csv_file, index=False)

        # Download link
        st.download_button(
            label="📥 Download Qualified Stocks CSV",
            data=result_df.to_csv(index=False).encode("utf-8"),
            file_name="qualified_stocks.csv",
            mime="text/csv"
        )
    else:
        st.error("❌ No stocks satisfied the conditions today.")

   
        progress_bar.progress((idx + 1) / total)

    # ---- Final Output ----
    st.subheader("✅ Qualified Stocks (Ascending CPR + Breakout)")
    if qualified_stocks:
        st.write(qualified_stocks)
    else:
        st.write("No stocks matched the criteria today.")


# end of today'cpr data
# comment code this
# uploaded_file = st.file_uploader("📂 Upload your stock list CSV", type=["csv"])

# if uploaded_file is not None:

#     stocks_df = pd.read_csv(uploaded_file)
#     stocks = stocks_df["Symbol"].tolist()

#     # Results list
#     qualified_stocks = []

#     # Today's date
#     today = datetime.today().date()

#     progress_bar = st.progress(0)
#     total = len(stocks)

#     for idx, ticker in enumerate(stocks):
#         try:
#             # --------------------------
#             # Step 1: Daily Data for CPR
#             # --------------------------
#             daily = yf.download(ticker, period="15d", interval="1d")
#             #daily = daily[daily.index.date < today]

#             if len(daily) == 0:
#                 continue  # not enough data

#             # Yesterday's OHLC
#             yday_high = float(daily["High"].iloc[-2])
#             #st.write("Ydayhigh",yday_high)
#             yday_low = float(daily["Low"].iloc[-2])
#             yday_close = float(daily["Close"].iloc[-2])

#             # CPR Calculation
#             P = (yday_high + yday_low + yday_close) / 3
#             BC = (yday_high + yday_low) / 2
#             TC = 2 * P - BC

#             # Check ascending CPR
#             if not (BC < P < TC):
#                 continue

#             # --------------------------
#             # Step 2: Intraday 5-min Data
#             # --------------------------
#             intraday = yf.download(
#                 ticker,
#                 start=daily.index[-1].date(),
#                 end=daily.index[-1].date() + timedelta(days=1),
#                 interval="5m"
#             ).reset_index()

#             if intraday.empty:
#                 continue

#             # First 5-min candle
#             first_candle = intraday.iloc[0]
#             first_open = float(first_candle["Open"])
#             first_close = float(first_candle["Close"])

#             # Check condition
#             if (first_close > first_open) and (first_close > yday_high):
#                 qualified_stocks.append(ticker)

#         except Exception as e:
#             st.warning(f"⚠️ Error processing {ticker}: {e}")
#             continue

#         progress_bar.progress((idx + 1) / total)

#     # --------------------------
#     # Step 3: Results
#     # --------------------------
#     if qualified_stocks:
#         st.success("✅ Stocks satisfying conditions:")
#         result_df = pd.DataFrame(qualified_stocks, columns=["Qualified Stocks"])
#         st.dataframe(result_df)

#         # Save to CSV
#         csv_file = "qualified_stocks.csv"
#         result_df.to_csv(csv_file, index=False)

#         # Download link
#         st.download_button(
#             label="📥 Download Qualified Stocks CSV",
#             data=result_df.to_csv(index=False).encode("utf-8"),
#             file_name="qualified_stocks.csv",
#             mime="text/csv"
#         )
#     else:
#         st.error("❌ No stocks satisfied the conditions today.")
# else:
#     st.info("👆 Please upload a stock list CSV file (with a 'Symbol' column).")    
# Put input widgets inside col1
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    ticker = st.text_input("Enter Stock Symbol (e.g., ASIANPAINT.NS):", "ASIANPAINT.NS")
with col2:
     period = st.text_input("Enter Daily Data Period (e.g., 30d):", "30d")
with col3:
     intraday_interval = st.selectbox("Intraday Interval:", ["5m", "15m", "30m", "60m"], index=0)
with col4:
     vol_filter = st.selectbox("Apply Volume Breakout Filter?", ["No", "Yes"], index=0)

if st.button("Run Analysis"):
    # --------------------------
    # Step 1: Get Daily Data (Yesterday's OHLC)
    # --------------------------
    daily = yf.download(ticker, period=period, interval="1d")
    if daily.empty or len(daily) < 2:
        st.error("Not enough daily data to calculate yesterday's CPR.")
        st.stop()

    daily = daily[daily.index.date < datetime.today().date()]
    yday = daily.iloc[-1]
    yday_high = float(yday["High"])
    yday_low = float(yday["Low"])
    yday_close = float(yday["Close"])

    # --------------------------
    # Step 2: Yesterday CPR
    # --------------------------
    pivot_y = (yday_high + yday_low + yday_close) / 3
    bc_y = (yday_high + yday_low) / 2
    tc_y = 2 * pivot_y - bc_y
    r1 = (2 * pivot_y) - yday_low
    s1 = (2 * pivot_y) - yday_high
    r2 = pivot_y + (yday_high - yday_low)
    s2 = pivot_y - (yday_high - yday_low)

    st.write(f"**Yesterday CPR:** Pivot={pivot_y:.2f}, BC={bc_y:.2f}, TC={tc_y:.2f}, R1={r1:.2f}, R2={r2:.2f}, S1={s1:.2f}, S2={s2:.2f}")

    # --------------------------
    # Step 3: Today's Intraday Data
    # --------------------------
    today = datetime.today().date()
    intraday = yf.download(
        ticker,
        start=today,
        end=today + timedelta(days=1),
        interval=intraday_interval
    ).reset_index()

    if intraday.empty:
        st.error("No intraday data found for today.")
        st.stop()

    if isinstance(intraday.columns, pd.MultiIndex):
        intraday.columns = intraday.columns.get_level_values(0)

    intraday = intraday.dropna(subset=["Open", "High", "Low", "Close"])

    # Convert timezone
    tz = "Asia/Kolkata" if ticker.endswith(".NS") else "America/New_York"
    intraday["Datetime"] = pd.to_datetime(intraday["Datetime"], utc=True).dt.tz_convert(tz)

    # --------------------------
    # Step 4: First Candle Breakout Check
    # --------------------------
    first_candle = intraday.iloc[0]
    first_close = first_candle["Close"]

    breakout = False
    if first_close > yday_high:
        if vol_filter == "Yes":
            avg_vol_10d = float(daily["Volume"].tail(7).mean())
            if first_candle["Volume"] > avg_vol_10d:
                breakout = True
            else:
                st.warning("⚠️ Volume not sufficient for breakout")
        else:
            breakout = True

    if breakout:
        st.success(f"✅ First candle closed above yesterday's high ({yday_high:.2f}) - Breakout Confirmed!")
    else:
        st.info(f"First candle close ({first_close:.2f}) below yesterday's high ({yday_high:.2f}) - No Breakout")

    # --------------------------
    # Step 5: Plot
    # --------------------------
    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=intraday["Datetime"],
        open=intraday['Open'],
        high=intraday['High'],
        low=intraday['Low'],
        close=intraday['Close'],
        name="Candles"
    ))

    # Yesterday High
    fig.add_hline(y=yday_high, line=dict(color="blue", dash="dash"), annotation_text=f"Yday High: {yday_high:.2f}")

    # CPR Zone
    cpr_color = "green" if first_close > pivot_y else "yellow"
    fig.add_shape(
        type="rect",
        x0=intraday["Datetime"].iloc[0],
        x1=intraday["Datetime"].iloc[-1],
        y0=bc_y,
        y1=tc_y,
        fillcolor=cpr_color,
        opacity=0.2,
        layer="below",
        line_width=0
    )

    # Mark Breakout
    if breakout:
        fig.add_trace(go.Scatter(
            x=[first_candle["Datetime"]],
            y=[first_candle["Close"]],
            mode="markers",
            marker=dict(color="orange", size=14, symbol="star"),
            name="Breakout"
        ))

    fig.update_layout(
        title=f"{ticker} - First Candle CPR Breakout Check",
        xaxis_title=f"Time ({tz})",
        yaxis_title="Price",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
        xaxis=dict(type="date", tickformat="%H:%M")
    )

    st.plotly_chart(fig, use_container_width=True)