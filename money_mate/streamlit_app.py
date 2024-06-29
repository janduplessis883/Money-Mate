import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.sidebar.header("Money-Mate")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read(
    worksheet="Personal Account Transactions",
    ttl="10m",
)

budget = conn.read(
    worksheet="Budget",
    ttl="10m",
)

st.header("Money-Mate")
st.dataframe(data)
st.dataframe(budget)
