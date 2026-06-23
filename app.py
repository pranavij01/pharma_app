import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide") # Use a wide layout for better dashboard presentation

# --- 1. Load Data ---
@st.cache_data # Cache data loading to improve performance
def load_data():
    try:
        df = pd.read_excel('Pharmacy_data.xlsx')

        # --- 2. Data Preprocessing (as done in Colab) ---
        df['Date'] = pd.to_datetime(df['DateKey'].astype(str), format='%Y%m%d')

        regions = ['North', 'South', 'East', 'West']
        store_sizes = ['Small', 'Medium', 'Large']

        df['Region'] = df['PharmacyID'].apply(lambda x: regions[int(x[2:]) % len(regions)])
        df['StoreSize'] = df['PharmacyID'].apply(lambda x: store_sizes[int(x[2:]) % len(store_sizes)])
        
        return df
    except FileNotFoundError:
        st.error("Error: 'Pharmacy_data.xlsx' not found. Please ensure the file is in the same directory as the script.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading or preprocessing the data: {e}")
        st.stop()

df = load_data()

# --- Streamlit App Layout ---
st.title("Pharmacy Revenue Dashboard")

# Sidebar filters
st.sidebar.header("Filter Options")
selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

selected_storesizes = st.sidebar.multiselect(
    "Select Store Size(s)",
    options=df['StoreSize'].unique(),
    default=df['StoreSize'].unique()
)

selected_promo_flags = st.sidebar.multiselect(
    "Select Promotion Status",
    options=df['PromoFlag'].unique(),
    default=df['PromoFlag'].unique()
)

# Apply filters
filtered_df = df[
    df['Region'].isin(selected_regions) &
    df['StoreSize'].isin(selected_storesizes) &
    df['PromoFlag'].isin(selected_promo_flags)
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # --- Visualizations ---
    st.header("Revenue Overview")

    # Total Revenue Card
    total_revenue = filtered_df['RevenueEUR'].sum()
    st.metric(label="Total Revenue (EUR)", value=f"{total_revenue:,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        # Revenue by Region
        revenue_by_region = filtered_df.groupby('Region')['RevenueEUR'].sum().reset_index()
        fig_region = px.bar(
            revenue_by_region,
            x='Region',
            y='RevenueEUR',
            title='Revenue by Region',
            color='Region'
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with col2:
        # Revenue by Store Size
        revenue_by_storesize = filtered_df.groupby('StoreSize')['RevenueEUR'].sum().reset_index()
        # Ensure consistent order for store sizes
        size_order = ['Small', 'Medium', 'Large']
        revenue_by_storesize['StoreSize'] = pd.Categorical(revenue_by_storesize['StoreSize'], categories=size_order, ordered=True)
        revenue_by_storesize = revenue_by_storesize.sort_values('StoreSize')

        fig_storesize = px.bar(
            revenue_by_storesize,
            x='StoreSize',
            y='RevenueEUR',
            title='Revenue by Store Size',
            color='StoreSize'
        )
        st.plotly_chart(fig_storesize, use_container_width=True)

    # Revenue by Promotion Status (Pie Chart)
    st.header("Revenue by Promotion Status")
    revenue_by_promo = filtered_df.groupby('PromoFlag')['RevenueEUR'].sum().reset_index()
    fig_promo = px.pie(
        revenue_by_promo,
        values='RevenueEUR',
        names='PromoFlag',
        title='Revenue Distribution by Promotion Status'
    )
    st.plotly_chart(fig_promo, use_container_width=True)
