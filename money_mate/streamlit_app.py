import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import altair as alt

from money_mate.utils import *


# Set the page configuration to have a wide layout and the sidebar collapsed on load
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Function to check passcode
def check_passcode():
    passcode = st.secrets["passcode"]["pin"]
    entered_passcode = st.text_input("Enter passcode:", type="password")
    if st.button("Submit"):
        if entered_passcode == passcode:
            st.session_state["authenticated"] = True
        else:
            st.write()
            st.write()
            ui.badges(badge_list=[("Incorrect Passcode, please try again.", "default")], class_name="flex gap-2", key="error1")
            st.toast(body="Incorrect Password", icon="‼️")

# Check if the user is authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
        c1, c2, c3 = st.columns(3)

        with c2:
            #st.image("images/private.png")
            st.image("images/private_flat.png")
            st.markdown(f"# ![Protected](https://img.icons8.com/pastel-glyph/64/fingerprint.png) Protected Content")
            check_passcode()


else:
    st.markdown("# ![Money-Mate](https://img.icons8.com/dotty/80/coins.png) Money-Mate")

    # -- Configure Sidebar ---------------------------------------------------------------------------------------------

    st.sidebar.markdown("# Settings")



    # -- END Configure Sidebar -----------------------------------------------------------------------------------------

    tabs = ui.tabs(options=['Account Summary', 'Budget', 'Account History', 'View | Update - Budget', 'View | Update - Bank Statement'], default_value='Account Summary', key="tab_bar1")

    gsheets = GSheetsConnection(...)
    # Continue with the rest of your app

    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)

    data = conn.read(
        worksheet="Personal Account Transactions",
        ttl="10m",
    )
    data = prep_account_statement(data)

    regular_expenses = conn.read(
        worksheet="Budget",
        ttl="10m",
    )
    budget = prep_budget(regular_expenses)
    filtered_bank_statement, days_remaining = prep_statement_import_to_budget(data)
    current = generate_budget_df(filtered_bank_statement, budget)
    # Return Budget Metrics
    total_budget, income_value, budget_used_sum, over_spent, remaining_budget, daily_budget, projected_disposable_income, actual_disposable_income = prep_budget_metrics(current, days_remaining)
    current_minus_income = budget_df_min_income(current)







    if tabs == "Account Summary":
        st.subheader("Account Summary")
        st.toast(body="""**Account Summary** - Monzo Bank""", icon="💷")




    elif tabs == "Budget":
        st.subheader("Budget")
        st.toast(body="""**Monthly Budget** to date.""", icon="😀")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="Total Monthly Budget", value=str(total_budget))
        c2.metric(label="Budget Used this Month", value=str(budget_used_sum))
        c3.metric(label="Remaining Allocation", value=str(remaining_budget))
        c4.metric(label="Anticipated Surplus", value=str(projected_disposable_income))

        # Create the horizontal bar plot
        plt.figure(figsize=(20, 6), dpi=300)
        colors = ['#ad2c6a' if val >= 0 else '#f3bd66' for val in current_minus_income['Diff']]

        bars = plt.barh(current_minus_income['categories'], current_minus_income['Diff'], color=colors)

        # Add data labels inside the bars
        for bar in bars:
            plt.text(
                bar.get_width() if bar.get_width() < 0 else bar.get_width() + 1,
                bar.get_y() + bar.get_height() / 2,
                f'{bar.get_width():.2f}',
                va='center',
                ha='right' if bar.get_width() < 0 else 'left',
                color='black'
            )

        # Set labels and title
        plt.xlabel('Difference')
        plt.ylabel('Categories')
        plt.title('Budget Difference by Category')
        plt.gca().invert_yaxis()  # To display the highest values at the top

        # Remove borders
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        # Add grid with specified linewidth and alpha
        plt.grid(True, linewidth=0.5, alpha=0.6)
        plt.tight_layout()
        st.pyplot(plt)



        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="Over Budget to date", value=str(over_spent))
        c2.metric(label="Realized Surplus", value=str(actual_disposable_income))
        c4.metric(label="Remaining Daily Budget", value=str(daily_budget))

        st.divider()
        switch_value1 = ui.switch(default_checked=False, label="Show Budget Calculation", key="switch1")
        if switch_value1:
            st.dataframe(current_minus_income)
        switch_value2 = ui.switch(default_checked=False, label="Show Bank Statement", key="switch2")
        if switch_value2:
            st.dataframe(filtered_bank_statement)

    elif tabs == "Account History":
        st.subheader("Account History")
        st.toast(body="""Viewing **Income & Expenses History**""", icon="📈")

    elif tabs == "View | Update - Budget":
        st.subheader("Budget Documents")
        st.toast(body="""Viewing **Budget DataFrames**""", icon="🔢")
        with st.expander(label="Budget - DataFrame", icon="🔢"):
            st.dataframe(budget)

        with st.expander(label="Budget prepped with Statement Info - DataFrame", icon="🔢"):
            st.dataframe(current)

        with st.expander(label="Budget - Google Sheet", icon="📋"):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?gid=1571834654#gid=1571834654"
            st.components.v1.html(f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>', height=600)


    elif tabs == "View | Update - Bank Statement":
        st.subheader("Bank Statements")
        st.toast(body="""Viewing **Bank Statements - Dataframes**""", icon="🔢")
        with st.expander(label="Account Statement - DataFrame", icon="🔢"):
            st.dataframe(data)

        with st.expander(label="Account Statement for Budget - DataFrame", icon="🔢"):
            st.dataframe(filtered_bank_statement)

        with st.expander(label="Account Statement - Google Sheet", icon="📋"):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?usp=sharing"
            st.components.v1.html(f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>', height=600)

# https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?usp=sharing
