"""
Stock Research App - Week-over-Week Analysis
A Streamlit application for analyzing stock performance with statistical insights.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import our modules
from data.stock_fetcher import (
    fetch_stock_data, 
    fetch_max_stock_data, 
    get_latest_price, 
    get_stock_info
)
from data.calculator import (
    calculate_weekly_returns,
    calculate_multi_timeframe_stats,
    get_timeframe_data,
    predict_current_week_price,
    predict_future_week_price
)
from utils.stats import calculate_statistics
from utils.ui_components import (
    display_stock_info,
    display_timeframe_comparison,
    display_prediction_metrics
)
from visualizations.plots import create_histogram

# Page configuration
st.set_page_config(
    page_title="Stock Research App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application interface"""
    st.title("📈 Stock Research App")
    st.markdown("**Weekly Returns Analysis - Week-over-Week Stock Performance**")
    
    # Sidebar inputs
    st.sidebar.header("Analysis Parameters")
    
    # Stock symbol input
    stock_symbol = st.sidebar.text_input(
        "Stock Symbol", 
        value="AAPL", 
        help="Enter a valid stock ticker (e.g., AAPL, MSFT, GOOGL)"
    ).upper()
    
    # Analysis type selection
    analysis_type = st.sidebar.radio(
        "Analysis Type",
        ["Multi-Timeframe Analysis", "Custom Date Range"],
        help="Choose between automatic multi-timeframe analysis or custom date range"
    )
    
    # Weeks ahead selection (always visible)
    st.sidebar.markdown("---")
    weeks_ahead = st.sidebar.selectbox(
        "🔮 Prediction Timeframe",
        options=[1, 2, 3, 4, 5, 6, 8, 10, 12],
        index=0,
        help="Select how many weeks ahead to predict with proper compounding"
    )
    
    if analysis_type == "Custom Date Range":
        # Date range selection
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365),
                help="Select the start date for analysis"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                help="Select the end date for analysis"
            )
        
        # Analysis button for custom range
        if st.sidebar.button("Run Custom Analysis", type="primary"):
            if stock_symbol and start_date < end_date:
                run_stock_analysis(stock_symbol, start_date, end_date, weeks_ahead)
            else:
                st.error("Please enter a valid stock symbol and date range.")
    
    else:
        # Multi-timeframe analysis button
        if st.sidebar.button("Run Multi-Timeframe Analysis", type="primary"):
            if stock_symbol:
                run_multi_timeframe_analysis(stock_symbol, weeks_ahead)
            else:
                st.error("Please enter a valid stock symbol.")
    
    # Instructions
    st.markdown("""
    ### How to Use
    1. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
    2. Choose analysis type:
       - **Multi-Timeframe**: Automatic weekly returns analysis across 1yr, 3yr, 5yr, 10yr, and max available data
       - **Custom Date Range**: Specify your own start and end dates for weekly returns analysis
    3. Click the analysis button to generate results
    
    ### Key Features - Weekly Returns Focus
    - **Multi-Timeframe Weekly Analysis**: Compare weekly return performance across different time horizons
    - **Risk-Adjusted Weekly Returns**: See weekly return per unit of risk for each time period
    - **Comprehensive Company Info**: Market cap, financial ratios, business description
    - **Multi-Week Price Predictions**: Predict prices 1-12 weeks ahead with proper compounding
    - **Holiday Handling**: Uses closest trading day to week end for holiday weeks
    - **Interactive Visualizations**: Histogram showing weekly return distribution
    
    ℹ️ **Note**: All return calculations are week-over-week (Friday close to Friday close, or last trading day of each week)
    """)


def run_stock_analysis(symbol: str, start_date: datetime, end_date: datetime, weeks_ahead: int):
    """
    Run complete stock analysis workflow for custom date range
    
    Args:
        symbol: Stock ticker symbol
        start_date: Analysis start date
        end_date: Analysis end date
        weeks_ahead: Number of weeks ahead to predict
    """
    with st.spinner(f"Fetching data for {symbol}..."):
        # Fetch stock data
        stock_data = fetch_stock_data(symbol, start_date, end_date)
        stock_info = get_stock_info(symbol)
        
        if stock_data.empty:
            return
        
        # Calculate weekly returns
        weekly_returns = calculate_weekly_returns(stock_data)
        
        if weekly_returns.empty:
            st.warning("Not enough data to calculate weekly returns.")
            return
        
        # Calculate statistics
        stats = calculate_statistics(weekly_returns['Weekly_Return_Pct'])
        
        # Get latest price for predictions
        latest_price = get_latest_price(symbol)
        
        # Display results
        st.success(f"Analysis complete for {symbol}")
        
        # Display stock information
        display_stock_info(stock_info, symbol)
        
        st.markdown("---")  # Divider
        
        # Statistics display
        st.subheader("📈 Weekly Return Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average Weekly Return", f"{stats['average']:.2f}%")
        with col2:
            st.metric("Minimum Weekly Return", f"{stats['minimum']:.2f}%")
        with col3:
            st.metric("Maximum Weekly Return", f"{stats['maximum']:.2f}%")
        with col4:
            st.metric("Weekly Volatility", f"{stats['std_dev']:.2f}%")
        
        # Multi-Week Price Predictions
        if latest_price:
            st.subheader("📊 Multi-Week Price Predictions")
            
            predictions = predict_future_week_price(latest_price, stats, weeks_ahead)
            
            if predictions:
                display_prediction_metrics(predictions)
                
                # Add disclaimer
                st.info("""
                ⚠️ **Disclaimer**: These predictions are based purely on historical weekly return patterns 
                and should not be used as financial advice. Actual stock prices are influenced by many 
                factors not captured in this analysis including market conditions, company news, 
                economic events, and other unpredictable variables.
                """)
        
        # Histogram
        st.subheader("📊 Return Distribution")
        fig = create_histogram(weekly_returns['Weekly_Return_Pct'], symbol)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        with st.expander("View Weekly Returns Data"):
            st.dataframe(
                weekly_returns.round(2),
                use_container_width=True
            )
        
        # Summary insights
        st.subheader("📋 Analysis Summary")
        positive_weeks = (weekly_returns['Weekly_Return_Pct'] > 0).sum()
        total_weeks = len(weekly_returns)
        win_rate = (positive_weeks / total_weeks) * 100
        
        st.write(f"""
        - **Total weeks analyzed**: {total_weeks}
        - **Positive weeks**: {positive_weeks} ({win_rate:.1f}%)
        - **Negative weeks**: {total_weeks - positive_weeks} ({100-win_rate:.1f}%)
        - **Average weekly return**: {stats['average']:.2f}%
        - **Volatility (std dev)**: {stats['std_dev']:.2f}%
        """)


def run_multi_timeframe_analysis(symbol: str, weeks_ahead: int):
    """
    Run multi-timeframe analysis using maximum available data
    
    Args:
        symbol: Stock ticker symbol
        weeks_ahead: Number of weeks ahead to predict
    """
    with st.spinner(f"Fetching maximum available data for {symbol}..."):
        # Fetch maximum available stock data
        full_stock_data = fetch_max_stock_data(symbol)
        stock_info = get_stock_info(symbol)
        
        if full_stock_data.empty:
            st.error(f"No data available for {symbol}")
            return
        
        # Calculate multi-timeframe statistics
        timeframe_stats = calculate_multi_timeframe_stats(full_stock_data)
        
        if not timeframe_stats:
            st.error("Unable to calculate timeframe statistics")
            return
        
        # Display results
        st.success(f"Multi-timeframe analysis complete for {symbol}")
        
        # Show data availability info
        data_start = full_stock_data.index.min()
        data_end = full_stock_data.index.max()
        total_years = len(full_stock_data) / 252  # Approximate trading days per year
        
        st.info(f"""
        📅 **Data Availability**: {data_start.strftime('%Y-%m-%d')} to {data_end.strftime('%Y-%m-%d')} 
        ({total_years:.1f} years of trading data)
        """)
        
        # Display stock information
        display_stock_info(stock_info, symbol)
        
        st.markdown("---")  # Divider
        
        # Display multi-timeframe comparison
        display_timeframe_comparison(timeframe_stats, symbol)
        
        st.markdown("---")  # Divider
        
        # Multi-week price predictions based on most recent year data (for relevance)
        latest_price = get_latest_price(symbol)
        if latest_price and '1yr' in timeframe_stats and timeframe_stats['1yr']:
            st.subheader("📊 Multi-Week Price Predictions")
            st.caption("Based on most recent 1-year weekly return patterns")
            
            predictions = predict_future_week_price(latest_price, timeframe_stats['1yr'], weeks_ahead)
            
            if predictions:
                display_prediction_metrics(predictions)
                
                # Add disclaimer
                st.info("""
                ⚠️ **Disclaimer**: These predictions are based purely on historical weekly return patterns 
                from the past year and should not be used as financial advice. Actual stock prices are 
                influenced by many factors not captured in this analysis.
                """)
        
        # Visualization section
        st.subheader("📊 Weekly Return Distribution Comparison")
        
        # Create tabs for different timeframes
        available_periods = [period for period in ['1yr', '3yr', '5yr', '10yr', 'max'] 
                           if period in timeframe_stats and timeframe_stats[period]]
        
        if available_periods:
            tabs = st.tabs([period.upper() for period in available_periods])
            
            # Define the timeframes mapping for correct years
            timeframes_map = {'1yr': 1, '3yr': 3, '5yr': 5, '10yr': 10, 'max': None}
            
            for i, period in enumerate(available_periods):
                with tabs[i]:
                    # Get data for this period using the correct integer years
                    period_years = timeframes_map.get(period)
                    period_data = get_timeframe_data(full_stock_data, period_years)
                    
                    if not period_data.empty:
                        weekly_returns = calculate_weekly_returns(period_data)
                        if not weekly_returns.empty:
                            fig = create_histogram(weekly_returns['Weekly_Return_Pct'], 
                                                 f"{symbol} ({period.upper()})")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show period-specific summary
                            stats = timeframe_stats[period]
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Average", f"{stats['average']:.2f}%")
                            with col2:
                                st.metric("Volatility", f"{stats['std_dev']:.2f}%")
                            with col3:
                                st.metric("Risk-Adjusted", f"{stats['average']/stats['std_dev']:.2f}")
        
        # Analysis insights
        st.subheader("📋 Investment Insights")
        
        # Long-term vs short-term comparison
        if 'max' in timeframe_stats and '1yr' in timeframe_stats:
            max_stats = timeframe_stats['max']
            recent_stats = timeframe_stats['1yr']
            
            st.write(f"""
            ### Long-term vs Recent Weekly Performance
            - **Long-term average weekly return** ({max_stats['years_of_data']:.1f} years): {max_stats['average']:.2f}%
            - **Recent weekly performance** (1 year): {recent_stats['average']:.2f}%
            - **Weekly performance trend**: {"Recent weekly outperformance" if recent_stats['average'] > max_stats['average'] else "Below long-term weekly average"}
            
            ### Weekly Risk Profile
            - **Long-term weekly volatility**: {max_stats['std_dev']:.2f}%
            - **Recent weekly volatility**: {recent_stats['std_dev']:.2f}%
            - **Weekly risk trend**: {"Increased weekly volatility" if recent_stats['std_dev'] > max_stats['std_dev'] else "Lower weekly volatility"}
            """)


if __name__ == "__main__":
    main()