import os
import streamlit as st
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="FoodFlow AI Dashboard",
    layout="wide"
)

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database="ZOMATO",
        schema="MARTS",
        role="DBT_ROLE"
    )

@st.cache_data
def get_data():

    conn = get_connection()

    query = """
        SELECT *
        FROM ZOMATO.MARTS.MART_DAILY_CITY_REVENUE
    """

    df = conn.cursor().execute(query).fetch_pandas_all()

    conn.close()

    df.columns = [col.lower() for col in df.columns]

    return df


df = get_data()

st.title("FoodFlow AI Dashboard")
st.caption("Food delivery business analytics")

# -------------------------
# KPI calculations
# -------------------------

total_orders = df["orders"].sum()
total_gmv = df["gmv"].sum()
avg_aov = df["aov"].mean()
avg_cancel_rate = df["cancel_rate"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", f"{total_orders:,.0f}")
col2.metric("Total GMV", f"₹{total_gmv:,.0f}")
col3.metric("Average AOV", f"₹{avg_aov:,.2f}")
col4.metric("Avg Cancel Rate", f"{avg_cancel_rate:.2%}")

st.divider()

# -------------------------
# Orders by city
# -------------------------

st.subheader("Orders by City")

orders_by_city = (
    df.groupby("city", as_index=False)["orders"]
    .sum()
    .sort_values("orders", ascending=False)
    .head(10)
)

st.bar_chart(
    orders_by_city,
    x="city",
    y="orders"
)

# -------------------------
# Revenue by city
# -------------------------

st.subheader("Revenue by City")

revenue_by_city = (
    df.groupby("city", as_index=False)["gmv"]
    .sum()
    .sort_values("gmv", ascending=False)
    .head(10)
)

st.bar_chart(
    revenue_by_city,
    x="city",
    y="gmv"
)

# -------------------------
# Daily trend
# -------------------------

st.subheader("Daily GMV Trend")

daily_gmv = (
    df.groupby("order_date", as_index=False)["gmv"]
    .sum()
    .sort_values("order_date")
)

st.line_chart(
    daily_gmv,
    x="order_date",
    y="gmv"
)

# -------------------------
# Raw data
# -------------------------

with st.expander("View Data"):

    st.dataframe(
        df,
        hide_index=True
    )