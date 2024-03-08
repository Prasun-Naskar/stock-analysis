from datetime import date, timedelta
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
# Get today's date and format it
today = date.today()
end_date = today.strftime("%Y-%m-%d")

# Calculate start date as 2 years ago from today
start_date = today - timedelta(days=365)
start_date = start_date.strftime("%Y-%m-%d")

# Title of the Streamlit app
st.title("Live Stock-Data Performance Analysis")

company_symbol = st.text_input("Enter a company yfinance name e.g-(Apple = aapl):", placeholder="Enter company name",)
if company_symbol:
    try:
        # Fetch stock data using yfinance
        data = yf.download(company_symbol, start=start_date, end=end_date)
        ticker = yf.Ticker(company_symbol)
        market_data = yf.download('^GSPC', start=start_date, end=end_date)
        stock_info = ticker.info
        try:
            if 'marketCap' in stock_info:
                market_cap = ticker.info['marketCap']
                st.markdown(f"<h1 style='text-align: center; color: orange;'>Market Cap of the company "
                            f"-: {market_cap}</h1>", unsafe_allow_html=True)
                st.subheader(
                    "Market cap gives an indication of the size of the company and can be a measure of its "
                    "stability and potential growth.")
            else:
                st.write(f"No market cap data available for {company_symbol}")
        except Exception as e:
            print(f"Error fetching data: {e}")
        average_volume = data['Volume'].mean()
        st.markdown(f"<h1 style='text-align: center; color: blue;'>Average Trading Volume of the company"
                    f" -: {round(average_volume)}</h1>", unsafe_allow_html=True)
        st.subheader("Trading volume can indicate the level of interest and activity in the stock. "
                     "Higher volume typically suggests greater liquidity and investor interest.")
        st.subheader("  ")
        col1, col2, col3 = st.columns(3)
        # Display fetched data
        with col2:
            st.write(data['Close'].describe())
        with col3:
            st.write("Mean: The average closing price\n\n\n")
            st.write(
                "Standard Deviation: Measures the amount of variation or dispersion of closing prices\n\n\n")
            st.write("Median (50%): The middle value of the closing prices\n\n\n")
            st.write("75th Percentile: 75% of the closing prices are below this value\n\n\n")
        with col1:
            st.write("Count: The number of observations or trading days included in the dataset.\n\n\n\n"

                     "Minimum: The lowest closing price in the dataset\n\n"

                     "25th Percentile: 25% of the closing prices are below this value\n\n\n"

                     "Maximum: The highest closing price in the dataset")
        # Plotting the close prices
        figure1 = go.Figure(data=[go.Candlestick(x=data.index,
                                                 open=data["Open"],
                                                 high=data["High"],
                                                 low=data["Low"],
                                                 close=data["Close"])])
        figure1.update_layout(title="Time Series Analysis of stock prices")

        figure1.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        st.plotly_chart(figure1)
        st.subheader("A candlestick chart is a handy tool to analyze the price movements "
                     "of stock prices over the timeline with a slider .")
        try:
            if 'dividendYield' in stock_info:
                dividend_yield = ticker.info['dividendYield']
                st.markdown(f"<h1 style='text-align: center; color: yellow;'>Dividend Yield of the company"
                            f" -: {dividend_yield:.4f}</h1>", unsafe_allow_html=True)
                st.subheader("Dividend Yield: For dividend-paying stocks, the dividend yield can indicate the "
                             "return generated from dividends relative to the stock price.")
                st.subheader(
                    f"A dividend yield of {dividend_yield:.4f}, expressed as a percentage, means that for every"
                    f" dollar invested in the company's stock, investors would receive approximately"
                    f" {dividend_yield * 100:.2f} cents in dividends annually.")
            else:
                st.write(f"No dividend yield data available for {company_symbol}")
        except Exception as e:
            print(f"Error fetching data: {e}")
        data['Daily_Return'] = data['Close'].pct_change()
        fig = go.Figure()

        # Creating subplots to show momentum and buying/selling markers
        figure = make_subplots(rows=2, cols=1)
        figure.add_trace(go.Scatter(x=data.index,
                                    y=data['Close'],
                                    name='Close Price'))
        figure.add_trace(go.Scatter(x=data.index,
                                    y=data['Daily_Return'],
                                    name='Daily_Return',
                                    yaxis='y2'))

        # Adding the buy and sell signals
        figure.add_trace(go.Scatter(x=data.loc[data['Daily_Return'] > 0].index,
                                    y=data.loc[data['Daily_Return'] > 0]['Close'],
                                    mode='markers', name='Buy',
                                    marker=dict(color='green', symbol='triangle-up')))

        figure.add_trace(go.Scatter(x=data.loc[data['Daily_Return'] < 0].index,
                                    y=data.loc[data['Daily_Return'] < 0]['Close'],
                                    mode='markers', name='Sell',
                                    marker=dict(color='red', symbol='triangle-down')))

        figure.update_layout(title='Momentum Strategy',
                             xaxis_title='Date',
                             yaxis_title='Price')
        figure.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        figure.update_yaxes(title="Daily_Return", secondary_y=True)
        # Display plot
        st.plotly_chart(figure)
        st.subheader(
            "In the momentum strategy, we buy the stocks when the momentum is positive and sell the stocks "
            "when the momentum is negative, where momentum is the trend-line of daily returns.")
        volatility = data['Daily_Return'].std()
        daily_returns = data['Close'].pct_change().dropna()
        # Recalculating average daily return and standard deviation (risk)
        avg_daily_return = daily_returns.mean()
        st.markdown(f"<h1 style='text-align: center; color: violet;"
                    f"'>Average daily return over the period-: {avg_daily_return:.5f}</h1>",
                    unsafe_allow_html=True)
        st.subheader(f"An average daily return of {avg_daily_return:.5f} means that, on average, the stock's"
                     f" price increased by "
                     f"approximately {avg_daily_return * 100:.2f}% each trading day over the given period.")
        st.markdown(f"<h1 style='text-align: center; color: green;"
                    f"'>Volatility of daily returns -: {volatility:.4f}</h1>",
                    unsafe_allow_html=True)
        st.subheader(
            "Volatility measures the variability of stock prices over time. High volatility may indicate"
            " higher risk but also potential for higher returns.")
        st.subheader(f"A volatility of daily returns of {volatility:.4f}"
                     f" means that, on average, the daily returns of the "
                     f"stock (expressed as a percentage) have a"
                     f" standard deviation of approximately {volatility * 100:.2f}% "
                     f"over the given time period.")
        cumulative_return = (1 + data['Daily_Return']).cumprod() - 1
        l_c = cumulative_return.iloc[-1]
        fig2 = px.area(cumulative_return, x=cumulative_return.index, y=cumulative_return,
                       labels={'Date': 'Date', 'y': 'Daily Cumulative Return'},
                       title="Cumulative Return over the period")
        fig2.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        fig2.update_layout(title='Cumulative Daily Returns',
                           xaxis_title='Date', yaxis_title='Cumulative Daily Return',
                           legend=dict(x=0.02, y=0.95))
        st.plotly_chart(fig2)
        st.subheader(
            "Cumulative returns represent the total percentage change in the stock’s value over a given "
            "period, considering the compounding effect of daily returns.")
        st.subheader(f"A cumulative daily return of {l_c:.4f} means that, over the given period, the stock's "
                     f"price has increased by approximately {l_c * 100:.2f}% in total.")
        try:
            if 'trailingEps' in stock_info:
                latest_price = data['Close'].iloc[-1]
                latest_eps = ticker.info['trailingEps']
                pe_ratio = latest_price / latest_eps
                st.markdown(f"<h1 style='text-align: center;"
                            f" color: yellow;'>pe_ratio of the company -: {pe_ratio : 1f}</h1>",
                            unsafe_allow_html=True)
                st.subheader("The Price-to-Earnings Ratio (P/E ratio) compares"
                             " the current price of the stock to its"
                             " earnings per share, giving an indication of the stock's valuation relative "
                             "to its earnings."
                             f"A P/E ratio of {pe_ratio:.4f} means that for every dollar of earnings per share (EPS),"
                             f" investors are willing to pay approximately ${pe_ratio:.2f}.")
            else:
                st.write(f"No EPS data available for {company_symbol}")
        except Exception as e:
            print(f"Error fetching data: {e}")
        colors = {'Close': 'blue', 'MA10': 'green', 'MA20': 'red'}
        data['MA10'] = data['Close'].rolling(window=10).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        fig3 = px.line(data, x=data.index, y=['Close', 'MA10', 'MA20'],
                       title=f"{company_symbol} Moving Averages", color_discrete_map=colors)
        fig3.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        st.plotly_chart(fig3)
        st.subheader(
            "When the MA10 crosses above the MA20, it is considered a bullish signal indicating that the stock"
            " price will continue to rise. Conversely, when the MA10 crosses below the MA20, it is a bearish"
            " signal that the stock price will continue falling.")
        # S&P 500 index as the market benchmark
        market_data['Daily_Return'] = market_data['Close'].pct_change()
        cov = data['Daily_Return'].cov(market_data['Daily_Return'])
        var_market = market_data['Daily_Return'].var()
        beta = (cov / var_market)
        st.markdown(
            f"<h1 style='text-align: center; color: red;'>Beta score of the company -: {beta : .4f}</h1>",
            unsafe_allow_html=True)
        st.subheader(
            f"In the above output, the beta value is approximately {beta:.4f}. This beta value suggests "
            f"that the stock is estimated to be approximately {(beta - 1) * 100:.2f}% more volatile "
            f"or sensitive to market "
            f"movements (as represented by the S&P 500 index) compared to the overall market.")
    except Exception as e:
        st.error(f"Error fetching or plotting data: {e}")
