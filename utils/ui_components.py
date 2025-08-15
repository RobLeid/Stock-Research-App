"""
UI Components Module
Handles display functions and user interface components
"""

import streamlit as st
import pandas as pd
from typing import Dict
from utils.stats import format_large_number


def display_stock_info(stock_info: dict, symbol: str):
    """
    Display stock information in a formatted layout
    
    Args:
        stock_info: Dictionary with stock information
        symbol: Stock ticker symbol
    """
    st.subheader(f"📋 {symbol} - Company Information")
    
    # Company basics
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Company Name:** {stock_info.get('name', symbol)}")
        st.write(f"**Sector:** {stock_info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {stock_info.get('industry', 'N/A')}")
        st.write(f"**Country:** {stock_info.get('country', 'N/A')}")
        
    with col2:
        st.write(f"**Market Cap:** {format_large_number(stock_info.get('market_cap'))}")
        st.write(f"**Enterprise Value:** {format_large_number(stock_info.get('enterprise_value'))}")
        st.write(f"**Average Volume:** {stock_info.get('average_volume', 'N/A'):,}" if stock_info.get('average_volume') else "**Average Volume:** N/A")
        st.write(f"**Currency:** {stock_info.get('currency', 'USD')}")
    
    # Financial metrics
    with st.expander("📊 Financial Metrics"):
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            pe_ratio = stock_info.get('pe_ratio')
            st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
            
        with metric_col2:
            forward_pe = stock_info.get('forward_pe')
            st.metric("Forward P/E", f"{forward_pe:.2f}" if forward_pe else "N/A")
            
        with metric_col3:
            pb_ratio = stock_info.get('price_to_book')
            st.metric("Price/Book", f"{pb_ratio:.2f}" if pb_ratio else "N/A")
            
        with metric_col4:
            beta = stock_info.get('beta')
            st.metric("Beta", f"{beta:.2f}" if beta else "N/A")
    
    # 52-week range and dividend
    with st.expander("📈 Price Range & Dividend"):
        range_col1, range_col2, range_col3 = st.columns(3)
        
        with range_col1:
            high_52 = stock_info.get('fifty_two_week_high')
            st.metric("52-Week High", f"${high_52:.2f}" if high_52 else "N/A")
            
        with range_col2:
            low_52 = stock_info.get('fifty_two_week_low')
            st.metric("52-Week Low", f"${low_52:.2f}" if low_52 else "N/A")
            
        with range_col3:
            div_yield = stock_info.get('dividend_yield')
            st.metric("Dividend Yield", f"{div_yield*100:.2f}%" if div_yield else "N/A")
    
    # Company description
    description = stock_info.get('description', '')
    if description and len(description) > 50:
        with st.expander("🏢 Business Description"):
            st.write(description)


def display_timeframe_comparison(timeframe_stats: dict, symbol: str):
    """
    Display comparison of weekly return statistics across different timeframes
    
    Args:
        timeframe_stats: Dictionary with statistics for different timeframes
        symbol: Stock ticker symbol
    """
    st.subheader("📊 Multi-Timeframe Weekly Returns Analysis")
    
    if not timeframe_stats:
        st.warning("No timeframe data available for analysis.")
        return
    
    # Create comparison table
    comparison_data = []
    
    for period, stats in timeframe_stats.items():
        if not stats:
            continue
            
        comparison_data.append({
            'Period': period.upper(),
            'Avg Weekly Return (%)': f"{stats['average']:.2f}",
            'Min Weekly Return (%)': f"{stats['minimum']:.2f}",
            'Max Weekly Return (%)': f"{stats['maximum']:.2f}",
            'Weekly Volatility (%)': f"{stats['std_dev']:.2f}",
            'Weeks Analyzed': stats['count'],
            'Years of Data': f"{stats['years_of_data']:.1f}",
            'Start Date': stats['data_start'].strftime('%Y-%m-%d'),
            'End Date': stats['data_end'].strftime('%Y-%m-%d')
        })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display as formatted table
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Key insights
        st.markdown("### 🔍 Key Insights")
        
        # Find best and worst performing periods
        best_period = max(timeframe_stats.items(), 
                         key=lambda x: x[1]['average'] if x[1] else float('-inf'))
        worst_period = min(timeframe_stats.items(), 
                          key=lambda x: x[1]['average'] if x[1] else float('inf'))
        
        most_volatile = max(timeframe_stats.items(), 
                           key=lambda x: x[1]['std_dev'] if x[1] else float('-inf'))
        least_volatile = min(timeframe_stats.items(), 
                            key=lambda x: x[1]['std_dev'] if x[1] else float('inf'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"🏆 **Best Average Weekly Return**: {best_period[0].upper()} ({best_period[1]['average']:.2f}%)")
            st.write(f"📉 **Worst Average Weekly Return**: {worst_period[0].upper()} ({worst_period[1]['average']:.2f}%)")
            
        with col2:
            st.write(f"📈 **Most Volatile Weekly Returns**: {most_volatile[0].upper()} ({most_volatile[1]['std_dev']:.2f}%)")
            st.write(f"📊 **Least Volatile Weekly Returns**: {least_volatile[0].upper()} ({least_volatile[1]['std_dev']:.2f}%)")
        
        # Risk-adjusted returns (simple Sharpe-like ratio)
        st.markdown("### 📈 Risk-Adjusted Weekly Performance")
        risk_adjusted_data = []
        
        for period, stats in timeframe_stats.items():
            if not stats or stats['std_dev'] == 0:
                continue
                
            # Simple risk-adjusted return (return/volatility ratio)
            risk_adjusted_return = stats['average'] / stats['std_dev']
            risk_adjusted_data.append({
                'Period': period.upper(),
                'Risk-Adjusted Weekly Return': f"{risk_adjusted_return:.2f}",
                'Weekly Return per Unit Risk': f"{risk_adjusted_return:.3f}"
            })
        
        if risk_adjusted_data:
            risk_df = pd.DataFrame(risk_adjusted_data)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning("No valid timeframe data available for comparison.")


def display_prediction_metrics(predictions: dict):
    """
    Display price prediction metrics with enhanced multi-week information
    
    Args:
        predictions: Dictionary with prediction data
    """
    if not predictions:
        return
        
    # Show prediction timeframe info
    weeks_ahead = predictions.get('weeks_ahead', 1)
    target_date_str = predictions.get('target_date_str', 'Unknown')
    
    if weeks_ahead > 1:
        st.caption(f"📅 **Predictions for {weeks_ahead} weeks ahead - Target Date: {target_date_str}** (with proper compounding)")
    else:
        st.caption(f"📅 **Predictions for next week - Target Date: {target_date_str}**")
        
    # Create prediction display
    pred_col1, pred_col2, pred_col3, pred_col4 = st.columns(4)
    
    with pred_col1:
        st.metric(
            "Current Price", 
            f"${predictions['current_price']:.2f}",
            help="Most recent trading day close"
        )
    with pred_col2:
        expected_help = f"Based on average weekly return of {predictions.get('weekly_avg_return', 0):.2f}%"
        if weeks_ahead > 1:
            expected_help += f" compounded over {weeks_ahead} weeks"
        st.metric(
            "Expected (Avg)", 
            f"${predictions['expected_price']:.2f}",
            delta=f"{predictions['expected_change']:.2f}%",
            help=expected_help
        )
    with pred_col3:
        optimistic_help = f"Based on maximum weekly return of {predictions.get('weekly_max_return', 0):.2f}%"
        if weeks_ahead > 1:
            optimistic_help += f" compounded over {weeks_ahead} weeks"
        st.metric(
            "Optimistic (Max)", 
            f"${predictions['optimistic_price']:.2f}",
            delta=f"{predictions['optimistic_change']:.2f}%",
            help=optimistic_help
        )
    with pred_col4:
        pessimistic_help = f"Based on minimum weekly return of {predictions.get('weekly_min_return', 0):.2f}%"
        if weeks_ahead > 1:
            pessimistic_help += f" compounded over {weeks_ahead} weeks"
        st.metric(
            "Pessimistic (Min)", 
            f"${predictions['pessimistic_price']:.2f}",
            delta=f"{predictions['pessimistic_change']:.2f}%",
            help=pessimistic_help
        )
    
    # Show compounding explanation for multi-week predictions
    if weeks_ahead > 1:
        with st.expander("🧮 Compounding Calculation Details"):
            st.write(f"""
            **Proper Compounding Formula**: Current Price × (1 + Weekly Return)^{weeks_ahead}
            
            **Example with Average Return ({predictions.get('weekly_avg_return', 0):.2f}%)**:
            - Week 1: ${predictions['current_price']:.2f} × (1 + {predictions.get('weekly_avg_return', 0):.4f}/100) = ${predictions['current_price'] * (1 + predictions.get('weekly_avg_return', 0)/100):.2f}
            - Week {weeks_ahead}: ${predictions['current_price']:.2f} × (1.{abs(predictions.get('weekly_avg_return', 0)):04.2f})^{weeks_ahead} = ${predictions['expected_price']:.2f}
            
            **Total Expected Change**: {predictions['expected_change']:.2f}% over {weeks_ahead} weeks
            **Not Simply**: {predictions.get('weekly_avg_return', 0) * weeks_ahead:.2f}% (which would be {predictions.get('weekly_avg_return', 0) * weeks_ahead:.2f}% without compounding)
            """)