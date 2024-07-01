import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import altair as alt
import time

from utils import *



# Set the page configuration to have a wide layout and the sidebar collapsed on load
st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="Money-Mate")
st.logo('images/mmlogo.png')
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
            st.toast(body="Incorrect Password", icon=":material/lock_person:")

# Check if the user is authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
        c1, c2, c3 = st.columns(3)

        with c2:
            #st.image("images/private.png")
            st.image("images/private.png")
            st.markdown(f"# ![Protected](https://img.icons8.com/pastel-glyph/64/fingerprint.png) Protected Content")
            check_passcode()


else:
    st.markdown("# ![Money-Mate](https://img.icons8.com/dotty/80/coins.png) Money-Mate")

    # -- Configure Sidebar ---------------------------------------------------------------------------------------------

    st.sidebar.markdown("# Settings")



    # -- END Configure Sidebar -----------------------------------------------------------------------------------------

    tabs = ui.tabs(options=['Account Summary', 'Budget', 'Income & Expenses Report', 'View | Update - Budget', 'View | Update - Bank Statement'], default_value='Account Summary', key="tab_bar1")

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


    # Global button with metircs reminders
    if st.sidebar.button('Account Overview'):
        st.toast(f"""### Payday Countdown: {days_remaining}""", icon=":material/event:")
        time.sleep(1.5)
        st.toast(f"""**Remaining Budget**: £ {remaining_budget}""", icon=":material/forward_media:")
        time.sleep(1.5)
        st.toast(f"""**Daily Budget**: £ {daily_budget}""", icon=":material/light_mode:")
        time.sleep(2)



    if tabs == "Account Summary":
        st.subheader("Account Summary")
        st.toast(body="""**Account Summary** - Monzo Bank""", icon=":material/currency_exchange:")


        line_chart = alt.Chart(filtered_bank_statement).mark_line(interpolate='step-after', color='#ec924f').encode(
            x=alt.X('Date:T', axis=alt.Axis(grid=True)),
            y=alt.Y('Cumulative Amount:Q', axis=alt.Axis(grid=True))
        ).properties(
            width=600,
            height=400,
            title="Cumulative Amount Over Time"
        )

        # Red dashed line at y=0
        rule = alt.Chart(filtered_bank_statement).mark_rule(color='#bb3b54', strokeDash=[5,5]).encode(
            y=alt.datum(0)
        )

        # Combine the line chart and the rule
        chart = alt.layer(line_chart, rule)

        st.altair_chart(chart, use_container_width=True, theme="streamlit")



    elif tabs == "Budget":
        st.subheader("Budget")
        st.toast(body="""**Monthly Budget** to date""", icon=":material/star:")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="Total Monthly Budget", value="£ "+str(total_budget))
        c2.metric(label="Budget Used this Month", value="£ "+str(budget_used_sum))
        c3.metric(label="Remaining Allocation", value="£ "+str(remaining_budget))
        c4.metric(label="Anticipated Surplus", value="£ "+str(projected_disposable_income))


        bar_chart = alt.Chart(current_minus_income).mark_bar().encode(
            y=alt.Y("categories:N", axis=alt.Axis(title="Categories", grid=True)),
            x=alt.X("Diff:Q", axis=alt.Axis(title="Difference")),
            color=alt.condition(
                alt.datum.Diff > 0,
                alt.value("#3f799c"),  # The positive color (approximation of the purple in the example)
                alt.value("#f3c15f")  # The negative color (approximation of the orange in the example)
            )
        ).properties(
            width=600,
            height=500,  # Adjust the height to fit all categories properly
            title="Budget Difference by Category"
        )

        # Text labels
        text = bar_chart.mark_text(
            align='left',
            baseline='middle',
            dx=5,  # Nudges text to right so it doesn't appear on top of the bar
            color='black'  # Set text color to black
        ).encode(
            text=alt.Text('Diff:Q', format='.2f'),
            x=alt.X('Diff:Q',
                    axis=alt.Axis(title='Difference'),
                    stack=None,
                    scale=alt.Scale(domain=[-300, 300]),
                    impute=None),
            color=alt.condition(
                alt.datum.Diff > 0,
                alt.value("black"),  # The color of the text for positive bars
                alt.value("black")  # The color of the text for negative bars
            )
        )

        # Combine bar chart and text labels
        line_chart = alt.layer(bar_chart, text)

        st.altair_chart(line_chart, use_container_width=True, theme="streamlit")



        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="Over Budget to date", value="£ "+str(over_spent))
        c2.metric(label="Realized Surplus", value="£ "+str(actual_disposable_income))
        c3.metric(label="Payday in", value=str(days_remaining)+" days")
        c4.metric(label="Remaining Daily Budget", value="£ "+str(daily_budget))

        st.divider()
        switch_value1 = ui.switch(default_checked=False, label="Show Budget Calculation", key="switch1")
        if switch_value1:
            st.dataframe(current_minus_income)
        switch_value2 = ui.switch(default_checked=False, label="Show Bank Statement", key="switch2")
        if switch_value2:
            st.dataframe(filtered_bank_statement)

    elif tabs == "Income & Expenses Report":
        st.subheader("Income & Expenses Report")
        st.toast(body="""**Income & Expenses** Report""", icon=":material/shopping_cart_checkout:")

        select_list = list(current['categories'].unique())
        selected_categories = st.sidebar.multiselect(
            'Select **Categories** to Display',
            options=select_list,
            default=['Eating Out', 'Groceries', 'Travel']
        )
        select_years = list(data['year'].unique())
        show_year = st.sidebar.multiselect(
            'Select **Years** to Display',
            options=select_years,
            default=[2024]
        )

        select_month = list(data['month_name'].unique())
        show_month = st.sidebar.multiselect(
            'Select **Months** to Display',
            options=select_month,
            default=['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun', 'Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec'],
        )

        print_df = st.sidebar.checkbox(label="View Dataframe")

        filtered_data = data[
            (data["categories"].isin(selected_categories)) & (data["year"].isin(show_year) & (data["month_name"].isin(show_month)))
        ]
        total_spend = filtered_data["Amount"].sum().round(2)

        cat_amount_df = return_cat_amount_df(filtered_data)
        name_amount_df = return_name_amount_df(filtered_data)
        cat_amount_date_df_week = return_cat_amount_date_df(filtered_data, period="W")
        cat_amount_date_df_mth = return_cat_amount_date_df(filtered_data, period="M")
        cat_amount_date_df_year = return_cat_amount_date_df(filtered_data, period="Y")

        c1, c2 = st.columns(2)

        with c1:
            chart_cat = alt.Chart(cat_amount_df).mark_arc(innerRadius=60).encode(
                theta="Amount",
                color="categories:N",
            )
            # Display the chart in Streamlit
            st.altair_chart(chart_cat, use_container_width=True, theme="streamlit")

        with c2:
            chart_name = alt.Chart(name_amount_df).mark_arc(innerRadius=60).encode(
                theta="Amount",
                color="Name:N",
            )
            # Display the chart in Streamlit
            st.altair_chart(chart_name, use_container_width=True, theme="streamlit")
            st.metric(label="Total Spend", value="£ "+str(total_spend))


        st.subheader("Week")
        line_week = alt.Chart(cat_amount_date_df_week).mark_line(interpolate="monotone").encode(
            x="Date:T",
            y="Amount:Q",
            color="categories:N"
        )
        st.altair_chart(line_week, use_container_width=True, theme="streamlit")

        st.subheader("Month")
        line_mth = alt.Chart(cat_amount_date_df_mth).mark_line(interpolate="monotone", point=True).encode(
            x=alt.X("Date:T", axis=alt.Axis(grid=True)),
            y=alt.Y("Amount:Q", axis=alt.Axis(grid=True)),
            color="categories:N"
        )
        st.altair_chart(line_mth, use_container_width=True, theme="streamlit")
        st.subheader("Year")
        line_year = alt.Chart(cat_amount_date_df_year).mark_line(interpolate="monotone", point=True).encode(
            x="Date:T",
            y="Amount:Q",
            color="categories:N"
        )
        st.altair_chart(line_year, use_container_width=True, theme="streamlit")

        if print_df == True:
            st.divider()
            st.dataframe(cat_amount_date_df_mth)



    elif tabs == "View | Update - Budget":
        st.subheader("Budget Documents")
        st.toast(body="""**Budget** - DataFrames""", icon=":material/savings:")
        with st.expander(label="Budget - DataFrame", icon=":material/savings:"):
            st.dataframe(budget)

        with st.expander(label="Budget prepped with Statement Info - DataFrame", icon=":material/savings:"):
            st.dataframe(current)

        with st.expander(label="Budget - Google Sheet", icon=":material/savings:"):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?gid=1571834654#gid=1571834654"
            st.components.v1.html(f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>', height=600)


    elif tabs == "View | Update - Bank Statement":
        st.subheader("Bank Statements")
        st.toast(body="""**Bank Statements** - Dataframes""", icon=":material/credit_card:")
        with st.expander(label="Account Statement - DataFrame", icon=":material/credit_card:"):
            st.dataframe(data)

        with st.expander(label="Account Statement for Budget - DataFrame", icon=":material/credit_card:"):
            st.dataframe(filtered_bank_statement)

        with st.expander(label="Account Statement - Google Sheet", icon=":material/credit_card:"):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?usp=sharing"
            st.components.v1.html(f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>', height=600)

# https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?usp=sharing
