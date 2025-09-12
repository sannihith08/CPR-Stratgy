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
            yday_high =daily["High"].iloc[-2].item()
            yday_low = daily["Low"].iloc[-2].item()
            yday_close =daily["Close"].iloc[-2].item()

            # Day-before-yesterday OHLC
            dby_high = daily["High"].iloc[-3].item()
            dby_low = daily["Low"].iloc[-3].item()
            dby_close = daily["Close"].iloc[-3].item()

            # CPR for yesterday
            y_pivot = (yday_high + yday_low + yday_close) / 3
            y_bc = (yday_high + yday_low) / 2
            y_tc = 2 * y_pivot - y_bc

            # CPR for day-before-yesterday
            dby_pivot = (dby_high + dby_low + dby_close) / 3
            dby_bc = (dby_high + dby_low) / 2
            dby_tc = 2 * dby_pivot - dby_bc
            # ---- CPR Trend ----
            if (y_pivot > dby_pivot and y_bc > dby_bc and y_tc > dby_tc):
                cpr_trend = "Ascending"
            elif (y_pivot < dby_pivot and y_bc < dby_bc and y_tc < dby_tc):
                cpr_trend = "Descending"
            else:
                cpr_trend = "Sideways"

            # ---- CPR Type (for yesterday CPR) ----
            cpr_width = y_tc - y_bc
            cpr_pct = (cpr_width / y_pivot) * 100
            cpr_type = "Narrow" if cpr_pct < 0.25 else "Wide"
            
            # Ascending CPR check
            if not (y_pivot > dby_pivot and y_bc > dby_bc and y_tc > dby_tc):
                continue

            # ---- Step 2: Intraday 5-min ----
            intraday = yf.download(ticker, period="1d", interval="5m")
            if intraday is None or intraday.empty:
                continue

            intraday = intraday.reset_index()

            # First 5-min candle
            first_candle = intraday.iloc[0]
            first_open = float(first_candle["Open"])
            first_close = float(first_candle["Close"])
            yday_high = float(daily["High"].iloc[-2])

            # first_open = first_candle["Open"]
            # first_close = first_candle["Close"]

            # Breakout check (close above open + above yesterday's high)
            #if (first_close > first_open) and (first_close > yday_high):
            if first_close > yday_high :   
                qualified_stocks.append({
                    "Symbol": ticker,
                    "First Open": first_open,
                    "First Close": first_close,
                    "Yesterday High": yday_high,
                    "CPR Trend": cpr_trend,
                    "CPR-Type" :cpr_type
                })

        except Exception as e:
            st.warning(f"⚠️ Error processing {ticker}: {e}")
            continue

        progress_bar.progress((idx + 1) / total)

    # --------------------------
    # Step 3: Results
    # --------------------------
    if qualified_stocks:
        st.success("✅ Stocks satisfying conditions:")
        result_df = pd.DataFrame(qualified_stocks)
        st.dataframe(result_df)
        # result_df = pd.DataFrame(qualified_stocks, columns=["Qualified Stocks"])
        # st.dataframe(result_df)

        # Save to CSV
        csv_file = "qualified_stocks.csv"
        result_df.to_csv(csv_file, index=False)

        # # Download link
        # st.download_button(
        #     label="📥 Download Qualified Stocks CSV",
        #     data=result_df.to_csv(index=False).encode("utf-8"),
        #     file_name="qualified_stocks.csv",
        #     mime="text/csv"
        # )
    else:
        st.error("❌ No stocks satisfied the conditions today.")

   
        progress_bar.progress((idx + 1) / total)

    # # ---- Final Output ----
    # st.subheader("✅ Qualified Stocks (Ascending CPR + Breakout)")
    # if qualified_stocks:
    #     st.write(qualified_stocks)
    # else:
    #     st.write("No stocks matched the criteria today.")


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
    # Step 1: Get Daily Data (Yesterday + Day Before Yesterday)
    # --------------------------
    daily = yf.download(ticker, period="7d", interval="1d")
    if daily.empty or len(daily) < 3:
        st.error("Not enough daily data to calculate CPR trend.")
        st.stop()

    # Remove today if market not closed
    daily = daily[daily.index.date < datetime.today().date()]

    # Yesterday and Day Before Yesterday
    yday = daily.iloc[-1]
    dby = daily.iloc[-2]

    # --------------------------
    # Step 2: Yesterday CPR
    # --------------------------
    yday_high = float(yday["High"])
    yday_low = float(yday["Low"])
    yday_close = float(yday["Close"])

    pivot_y = (yday_high + yday_low + yday_close) / 3
    bc_y = (yday_high + yday_low) / 2
    tc_y = 2 * pivot_y - bc_y

    r1 = (2 * pivot_y) - yday_low
    s1 = (2 * pivot_y) - yday_high
    r2 = pivot_y + (yday_high - yday_low)
    s2 = pivot_y - (yday_high - yday_low)

    # --------------------------
    # Step 3: Day Before Yesterday CPR (for trend check)
    # --------------------------
    dby_high = float(dby["High"])
    dby_low = float(dby["Low"])
    dby_close = float(dby["Close"])

    pivot_dby = (dby_high + dby_low + dby_close) / 3
    bc_dby = (dby_high + dby_low) / 2
    tc_dby = 2 * pivot_dby - bc_dby

    # --------------------------
    # Step 4: CPR Trend Logic
    # --------------------------
    # if bc_y > bc_dby and tc_y > tc_dby:
    #     cpr_trend = "📈 Ascending CPR (Bullish)"
    # elif bc_y < bc_dby and tc_y < tc_dby:
    #     cpr_trend = "📉 Descending CPR (Bearish)"
    # elif bc_y > tc_dby and tc_y < bc_dby:
    #     cpr_trend = "📊 Inside Value CPR (Consolidation)"
    # elif tc_y < bc_dby or bc_y > tc_dby:
    #     cpr_trend = "🔄 Outside Value CPR (Volatile)"
    # else:
    #     cpr_trend = "⚖️ Neutral CPR"
    if bc_y > bc_dby and tc_y > tc_dby:
        cpr_trend = "📈 Ascending CPR (Bullish)"
    elif bc_y < bc_dby and tc_y < tc_dby:
        cpr_trend = "📉 Descending CPR (Bearish)"
    elif (bc_y >= bc_dby) and (tc_y <= tc_dby):
        cpr_trend = "📊 Inside Value CPR (Consolidation)"
    elif (bc_y < bc_dby and tc_y > tc_dby) or (bc_y > bc_dby and tc_y < tc_dby):
        cpr_trend = "🔄 Outside Value CPR (Volatile)"
    else:
        cpr_trend = "⚖️ Neutral CPR"

    st.write(f"**Yesterday CPR:** Pivot={pivot_y:.2f}, BC={bc_y:.2f}, TC={tc_y:.2f}")
    st.write(f"R1={r1:.2f}, R2={r2:.2f}, S1={s1:.2f}, S2={s2:.2f}")
    st.info(f"**CPR Trend:** {cpr_trend}")

    # --------------------------
    # Step 5: Today's Intraday Data
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
    # Step 6: First Candle Breakout Check
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
    # Step 7: Plot
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
    fig.add_shape(
        type="rect",
        x0=intraday["Datetime"].iloc[0],
        x1=intraday["Datetime"].iloc[-1],
        y0=bc_y,
        y1=tc_y,
        fillcolor="green" if first_close > pivot_y else "yellow",
        opacity=0.2,
        layer="below",
        line_width=0
    )

    # R1, R2, S1, S2 Lines
    fig.add_hline(y=r1, line=dict(color="purple", dash="dot"), annotation_text=f"R1 {r1:.2f}")
    fig.add_hline(y=r2, line=dict(color="purple", dash="dot"), annotation_text=f"R2 {r2:.2f}")
    fig.add_hline(y=s1, line=dict(color="red", dash="dot"), annotation_text=f"S1 {s1:.2f}")
    fig.add_hline(y=s2, line=dict(color="red", dash="dot"), annotation_text=f"S2 {s2:.2f}")

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
        title=f"{ticker} - First Candle CPR Breakout + Trend",
        xaxis_title=f"Time ({tz})",
        yaxis_title="Price",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
        xaxis=dict(type="date", tickformat="%H:%M")
    )

    st.plotly_chart(fig, use_container_width=True)





# --------------------------
# User Inputs
# --------------------------
# ticker = st.text_input("Enter Stock Symbol:", "HDFCBANK.NS")
# intraday_interval = st.selectbox("Intraday Interval:", ["5m", "15m", "30m", "60m"])
# vol_filter = st.selectbox("Apply Volume Filter for Breakout?", ["Yes", "No"])

# # --------------------------
# if st.button("Run New CPR Stratgy"):
    # --------------------------
    # Step 1: Get Daily Data (Yesterday + Day Before Yesterday)
    # --------------------------
    daily = yf.download(ticker, period="7d", interval="1d")
    if daily.empty or len(daily) < 2:
        st.error("Not enough daily data to calculate CPR.")
        st.stop()

    # Remove today if market not closed
    daily = daily[daily.index.date < datetime.today().date()]

    yday = daily.iloc[-1]   # Yesterday
    dby  = daily.iloc[-2]   # Day Before Yesterday (optional for trend)

    # --------------------------
    # Step 2: Yesterday CPR
    # --------------------------
    yday_high  = float(yday["High"])
    yday_low   = float(yday["Low"])
    yday_close = float(yday["Close"])

    pivot_y = (yday_high + yday_low + yday_close) / 3
    bc_y = (yday_high + yday_low) / 2
    tc_y = 2 * pivot_y - bc_y

    r1 = (2 * pivot_y) - yday_low
    s1 = (2 * pivot_y) - yday_high
    r2 = pivot_y + (yday_high - yday_low)
    s2 = pivot_y - (yday_high - yday_low)

    # --------------------------
    # Optional: CPR Trend
    # --------------------------
    dby_high  = float(dby["High"])
    dby_low   = float(dby["Low"])
    dby_close = float(dby["Close"])

    pivot_dby = (dby_high + dby_low + dby_close) / 3
    bc_dby = (dby_high + dby_low) / 2
    tc_dby = 2 * pivot_dby - bc_dby

    ascending_cpr = bc_y > bc_dby and tc_y > tc_dby
    cpr_trend = "📈 Ascending CPR (Bullish)" if ascending_cpr else "Not Ascending CPR"

    st.write(f"**Yesterday CPR:** Pivot={pivot_y:.2f}, BC={bc_y:.2f}, TC={tc_y:.2f}")
    st.write(f"R1={r1:.2f}, R2={r2:.2f}, S1={s1:.2f}, S2={s2:.2f}")
    st.info(f"**CPR Trend:** {cpr_trend}")

    # --------------------------
    # Step 3: Intraday Data Today
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
    tz = "Asia/Kolkata" if ticker.endswith(".NS") else "America/New_York"
    intraday["Datetime"] = pd.to_datetime(intraday["Datetime"], utc=True).dt.tz_convert(tz)

    # --------------------------
    # Step 4: 3-Candle Breakout Check (Ascending CPR)
    # --------------------------
    breakout = False
    if ascending_cpr:
        if len(intraday) < 3:
            st.warning("Not enough intraday candles for 3-candle pattern check")
        else:
            c1 = intraday.iloc[0]
            c2 = intraday.iloc[1]
            c3 = intraday.iloc[2]

            c1_green = c1["Close"] > c1["Open"]
            c2_red   = c2["Close"] < c2["Open"]
            c3_green = c3["Close"] > c3["Open"]

            breakout = c1_green and c2_red and c3_green and (c3["Close"] > yday_high) and (c3["Close"] > r1)

            # Apply volume filter if selected
            if vol_filter == "Yes":
                avg_vol_10d = float(daily["Volume"].tail(7).mean())
                if c3["Volume"] < avg_vol_10d:
                    breakout = False
                    st.warning("⚠️ Third candle volume not sufficient for breakout")

            if breakout:
                st.success(f"✅ 3-Candle Breakout Confirmed! Third candle closed at {c3['Close']:.2f} above Yday High {yday_high:.2f} and R1 {r1:.2f}")
            else:
                st.info("3-Candle breakout pattern not formed yet.")

    # --------------------------
    # Step 5: Plot Intraday Chart
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
    fig.add_shape(
        type="rect",
        x0=intraday["Datetime"].iloc[0],
        x1=intraday["Datetime"].iloc[-1],
        y0=bc_y,
        y1=tc_y,
        fillcolor="green" if ascending_cpr else "yellow",
        opacity=0.2,
        layer="below",
        line_width=0
    )

    # R1, R2, S1, S2 Lines
    fig.add_hline(y=r1, line=dict(color="purple", dash="dot"), annotation_text=f"R1 {r1:.2f}")
    fig.add_hline(y=r2, line=dict(color="purple", dash="dot"), annotation_text=f"R2 {r2:.2f}")
    fig.add_hline(y=s1, line=dict(color="red", dash="dot"), annotation_text=f"S1 {s1:.2f}")
    fig.add_hline(y=s2, line=dict(color="red", dash="dot"), annotation_text=f"S2 {s2:.2f}")

    # Mark Breakout
    if breakout:
        fig.add_trace(go.Scatter(
            x=[c3["Datetime"]],
            y=[c3["Close"]],
            mode="markers",
            marker=dict(color="orange", size=14, symbol="star"),
            name="Breakout"
        ))

    fig.update_layout(
        title=f"{ticker} - 3-Candle CPR Breakout + Trend",
        xaxis_title=f"Time ({tz})",
        yaxis_title="Price",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
        xaxis=dict(type="date", tickformat="%H:%M")
    )

    st.plotly_chart(fig, use_container_width=True)

