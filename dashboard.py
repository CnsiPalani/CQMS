import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from query import show_all_data
import random

def dashboard():
    """
    Displays an interactive dashboard for client queries using Streamlit.
    The dashboard includes:
    - A line chart showing the average resolution time (in days) of closed queries over time.
    - A bar chart displaying the frequency of different query types.
    - A pie chart illustrating the distribution of query statuses.
    Data is retrieved via `show_all_data()` and processed into a pandas DataFrame.
    Missing values are filled with zero, and resolution times are calculated for closed queries.
    Charts are rendered using matplotlib, seaborn, and Streamlit.
    Returns:
        None
    """
    data = show_all_data()
    df = pd.DataFrame(data, columns=[
        "query_id", "emailid", "mobilenumber", "query_heading", "query_description",
        "query_created_time", "status", "query_closed_time"
    ])

    # Fill missing values
    df = df.fillna(0)

    # Calculate resolution time in days
    df['Created Date'] = pd.to_datetime(df['query_created_time'])
    df['Resolved Date'] = pd.to_datetime(df['query_closed_time'])
    df['Resolution Time (days)'] = (df['Resolved Date'] - df['Created Date']).dt.days
    df['Resolution Time (days)'] = df['Resolution Time (days)'].fillna(0)

   
    # Line chart: Resolution time trends
    # st.subheader("📈 Resolution Time Trends")
    resolution_trend = df[df['status'] == 'Closed'].copy()
    resolution_trend['Resolved Date'] = pd.to_datetime(resolution_trend['Resolved Date'])
    trend_data = resolution_trend.groupby(resolution_trend['Resolved Date'].dt.date)['Resolution Time (days)'].mean().reset_index()

    fig1, ax1 = plt.subplots()
    ax1.plot(trend_data['Resolved Date'], trend_data['Resolution Time (days)'], marker='o')
    ax1.set_title('Average Resolution Time Over Time')
    ax1.set_xlabel('Resolved Date')
    ax1.set_ylabel('Resolution Time (days)')
    plt.xticks(rotation=45)
    #   st.pyplot(fig1)

    # Bar chart: Query type frequency
    # st.subheader("📊 Query Type Frequency")
    type_counts = df['query_heading'].value_counts().reset_index()
    type_counts.columns = ['Query Type', 'Count']

    fig2, ax2 = plt.subplots()
    sns.barplot(data=type_counts, x='Query Type', y='Count', ax=ax2)
    ax2.set_title('Frequency of Query Types')
    plt.xticks(rotation=45)
    # st.pyplot(fig2)

    # Pie chart: Status distribution
    # st.subheader("🗂️ Status Distribution")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    fig3, ax3 = plt.subplots()
    ax3.pie(status_counts['Count'], labels=status_counts['Status'], autopct='%1.1f%%', startangle=140)
    ax3.set_title('Distribution of Query Statuses')
    # st.pyplot(fig3)

    # Place charts in a row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<h2 style='font-size:1.2em;'>📈 Resolution Time Trends</h2>", unsafe_allow_html=True)
        st.pyplot(fig1)
    with col2:
        st.markdown("<h2 style='font-size:1.2em;'>📊 Query Type Frequency</h2>", unsafe_allow_html=True)
        st.pyplot(fig2)
    with col3:
        st.markdown("<h2 style='font-size:1.2em;'>🗂️ Status Distribution</h2>", unsafe_allow_html=True)
        st.pyplot(fig3)
    
    


    

   
   

    

    
