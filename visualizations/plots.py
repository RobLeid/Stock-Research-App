"""
Visualization Module
Handles all plotting and chart generation for weekly returns
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_histogram(returns: pd.Series, symbol: str) -> go.Figure:
    """
    Create histogram of weekly returns
    
    Args:
        returns: Series of weekly percentage returns
        symbol: Stock symbol for title
        
    Returns:
        Plotly figure object
    """
    fig = px.histogram(
        x=returns,
        nbins=20,
        title=f"{symbol} - Weekly Returns Distribution",
        labels={'x': 'Weekly Return (%)', 'y': 'Frequency'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="Weekly Return (%)",
        yaxis_title="Frequency",
        template="plotly_white"
    )
    
    # Add mean line
    mean_return = returns.mean()
    fig.add_vline(
        x=mean_return, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Mean: {mean_return:.2f}%"
    )
    
    return fig