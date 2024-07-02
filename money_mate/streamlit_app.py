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
from classification import *


# Set the page configuration to have a wide layout and the sidebar collapsed on load
st.set_page_config(
    layout="wide", initial_sidebar_state="collapsed", page_title="Money-Mate"
)
st.logo("images/mmlogo.png")


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
            ui.badges(
                badge_list=[("Incorrect Passcode, please try again.", "default")],
                class_name="flex gap-2",
                key="error1",
            )
            st.toast(body="Incorrect Password", icon=":material/lock_person:")


# Check if the user is authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    c1, c2, c3 = st.columns(3)

    with c2:
        # st.image("images/private.png")
        st.image("images/private.png")
        st.markdown(
            f"# ![Protected](https://img.icons8.com/pastel-glyph/64/fingerprint.png) Protected Content"
        )
        check_passcode()

else:
    st.markdown("# ![Money-Mate](https://img.icons8.com/dotty/80/coins.png) Money-Mate")

    # -- Configure Sidebar ---------------------------------------------------------------------------------------------

    st.sidebar.markdown("# Settings")
    # Function to clear cache and reload the page
    def clear_cache_and_reload():
        st.cache_data.clear()
        st.cache_resource.clear()
        st.experimental_rerun()

    # UI button to trigger cache clearing and page reload
    if st.sidebar.button("Clear Cache and Reload"):
        clear_cache_and_reload()
    # -- END Configure Sidebar -----------------------------------------------------------------------------------------

    tabs = ui.tabs(
        options=[
            "Account Summary",
            "Budget",
            "Income & Expenses Report",
            "View | Update - Budget",
            "View | Update - Bank Statement",
            "Settings",
        ],
        default_value="Account Summary",
        key="tab_bar1",
    )


    # Function to determine if data is being fetched from cache
    def is_data_loading(last_fetch_time, ttl_seconds):
        current_time = time.time()
        return (current_time - last_fetch_time) > ttl_seconds

    # Your existing setup
    gsheets = GSheetsConnection(...)

    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Time-to-live in seconds (10 minutes)
    ttl_seconds = 20 * 60

    # Initialize session state for fetch times if not already done
    if "last_fetch_personal_account" not in st.session_state:
        st.session_state.last_fetch_personal_account = 0
    if "last_fetch_budget" not in st.session_state:
        st.session_state.last_fetch_budget = 0

    # Read Personal Account Transactions
    data = conn.read(
        worksheet="Personal Account Transactions",
        ttl="20m",
    )

    # Process the data
    data = prep_account_statement(data)
    account_balance = get_account_balance(data)

    apply_adjustment = st.sidebar.toggle("Smoking Adjustment")

    if apply_adjustment:
        smoking_adjustment_amount = abs(calculate_smoking_adjustment(data))
        data = apply_smoking_adjustment(data)
        # Check if data is fresh and display toast if so
        if is_data_loading(st.session_state.last_fetch_personal_account, ttl_seconds):
            st.toast(
                f"**Smoking** adjustment → **£ {smoking_adjustment_amount}**", icon="🚬"
            )
            st.session_state.last_fetch_personal_account = time.time()

    # Read Budget
    regular_expenses = conn.read(
        worksheet="Budget",
        ttl="20m",
    )

    # Check if data is fresh and display toast if so
    if is_data_loading(st.session_state.last_fetch_budget, ttl_seconds):
        st.toast("**Budget** calculation! ✅", icon=":material/credit_card_gear:")
        st.session_state.last_fetch_budget = time.time()

    # Prepare budget
    budget = prep_budget(regular_expenses)
    filtered_bank_statement, days_remaining = prep_statement_import_to_budget(data)
    current = generate_budget_df(filtered_bank_statement, budget)

    # Return Budget Metrics
    (
        variable_expenses,
        total_budget,
        income_value,
        budget_used_sum,
        over_spent,
        remaining_budget,
        daily_allowance,
        projected_disposable_income,
        actual_disposable_income
    ) = prep_budget_metrics(current, days_remaining)
    current_minus_income = budget_df_min_income(current)

    # Global button with metircs reminders
    if st.sidebar.button("Account Overview"):
        st.toast(f"""### {days_remaining} days ➞ 🤑""", icon=":material/event:")
        time.sleep(1.5)
        st.toast(
            f"""**Remaining Budget**: £ {remaining_budget}""",
            icon=":material/forward_media:",
        )
        time.sleep(1.5)
        st.toast(
            f"""**Daily Allowance**: £ {daily_allowance}""", icon=":material/light_mode:"
        )

    if tabs == "Account Summary":
        st.header("Account Summary")

        st.metric("Monzo Account Balance", value="£ " + str(account_balance))

        line_chart = (
            alt.Chart(filtered_bank_statement)
            .mark_line(interpolate="step-after", color="#ec924f")
            .encode(
                x=alt.X("Date:T", axis=alt.Axis(grid=True)),
                y=alt.Y("Cumulative Amount:Q", axis=alt.Axis(grid=True)),
            )
            .properties(width=600, height=400, title="Cumulative Amount Over Time")
        )

        # Red dashed line at y=0
        rule = (
            alt.Chart(filtered_bank_statement)
            .mark_rule(color="#bb3b54", strokeDash=[5, 5])
            .encode(y=alt.datum(0))
        )

        # Combine the line chart and the rule
        chart = alt.layer(line_chart, rule)

        st.altair_chart(chart, use_container_width=True, theme="streamlit")

    elif tabs == "Budget":
        st.header("Budget")

        # Streamlit slider
        st.sidebar.header('Budget and Expense Tracker')
        st.sidebar.write('Adjust your variable expenses using the slider below:')
        variable_expenses_slider = st.sidebar.slider(
            'Variable Expenses',
            min_value=0,
            max_value=int(variable_expenses),
            value=int(variable_expenses) // 2
        )

        st.sidebar.markdown(f'You have selected **£ {variable_expenses_slider}** for your variable expenses.')

        # Use the slider value in your application
        # For example, update remaining budget based on slider value
        remaining_budget_adjusted = remaining_budget - variable_expenses_slider
        adjusted_remaining_budget = remaining_budget - (variable_expenses - variable_expenses_slider)
        adjusted_daily_allowance = (adjusted_remaining_budget / days_remaining).round(2) if days_remaining else 0
        st.sidebar.markdown(f'Adjusted remaining budget: **£ {remaining_budget_adjusted.round(2)}**')
        st.sidebar.markdown(f'Adjusted daily allowance: **£ {adjusted_daily_allowance}**')
        st.sidebar.divider()

        st.markdown(f"Salary: **£ {income_value}** - Budget: **£ {total_budget}** = Left-over: **£ {projected_disposable_income}**")
        st.markdown(f":blue[**Variable Expenses**: (Barber, Eating Out, Groceries, Holiday, Shopping, Smoking, Transport): **£ {variable_expenses}**] - :red[over-spent: **£ {over_spent}**] = **£ {(variable_expenses - over_spent).round(2)}**")
        st.markdown(f":red[Daily Allovance: **£ {daily_allowance}**]")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="Over Budget to date", value="£ " + str(over_spent))
        c2.metric(label="Realized Surplus", value="£ " + str(actual_disposable_income))
        c3.metric(label="Payday Countdown", value=str(days_remaining) + " days")
        c4.metric(label="Daily Allowance (factoring in Over-spend)", value="£ " + str(daily_allowance))


        # Define the domain for the x-axis to ensure it covers both Difference and Budget values
        x_domain = [
            min(
                current_minus_income["Diff"].min(), current_minus_income["Budget"].min()
            ),
            max(
                current_minus_income["Diff"].max(), current_minus_income["Budget"].max()
            ),
        ]

        if st.sidebar.toggle("Large Budget Chart"):
            chart_height = 600
            font_size = 14
        else:
            chart_height = 500
            font_size = 12
        # Create the base bar chart
        bar_chart = (
            alt.Chart(current_minus_income)
            .mark_bar()
            .encode(
                y=alt.Y(
                    "custom_category:N", axis=alt.Axis(title="Categories", grid=True)
                ),
                x=alt.X(
                    "Diff:Q",
                    axis=alt.Axis(title="Difference"),
                    scale=alt.Scale(domain=x_domain),
                ),
                color=alt.condition(
                    alt.datum.Diff > 0,
                    alt.value("#3f799c"),  # The positive color
                    alt.value("#f3c15f"),  # The negative color
                ),
            )
            .properties(
                width=800,
                height=chart_height,  # Adjust the height to fit all categories properly
                title="Budget Difference by Category",
            )
        )

        # Create the red dot layer for the budget
        budget_dots = (
            alt.Chart(current_minus_income)
            .mark_point(color="#bb271a", size=10)
            .encode(
                x=alt.X("Budget:Q", scale=alt.Scale(domain=x_domain)),
                y=alt.Y("custom_category:N", sort="-x"),
            )
        )

        # Text labels
        # Text labels with updated font size
        text = bar_chart.mark_text(
            align="left",
            baseline="middle",
            dx=5,  # Nudges text to right so it doesn't appear on top of the bar
            color="black",  # Set text color to black
            fontSize=font_size,  # Update font size here
        ).encode(
            text=alt.Text("Diff:Q", format=".2f"),
            x=alt.X(
                "Diff:Q",
                axis=alt.Axis(title="Difference"),
                stack=None,
                scale=alt.Scale(domain=x_domain),
                impute=None,
            ),
            y=alt.Y("custom_category:N", sort="-x"),
            color=alt.value("black"),  # Ensure text color is black
        )

        # Combine bar chart, budget dots, and text labels
        combined_chart = alt.layer(bar_chart, budget_dots, text).resolve_scale(
            x="shared"
        )

        # Display the combined chart in Streamlit
        st.altair_chart(combined_chart, use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="Total Monthly Budget", value="£ " + str(total_budget))
        c2.metric(label="Budget Used this Month", value="£ " + str(budget_used_sum))
        c3.metric(label="Remaining Allocation", value="£ " + str(remaining_budget))
        c4.metric(
            label="Anticipated Surplus", value="£ " + str(projected_disposable_income)
        )

        if st.sidebar.toggle("Show Bank Statement"):
            st.divider()
            st.subheader("Current Bank Statement")
            st.dataframe(filtered_bank_statement)

        if st.sidebar.toggle("Show Budget Calculation"):
            st.divider()
            st.subheader("Budget Calculation")
            st.dataframe(current_minus_income)

    elif tabs == "Income & Expenses Report":
        st.header("Income & Expenses Report")
        st.sidebar.divider()
        select_list = list(current["custom_category"].unique())
        selected_categories = st.sidebar.multiselect(
            "Select **Categories** to Display",
            options=select_list,
            default=["Eating Out", "Groceries", "Smoking"],
        )
        select_years = list(data["year"].unique())
        show_year = st.sidebar.multiselect(
            "Select **Years** to Display",
            options=select_years,
            default=[
                2024,
            ],
        )

        select_month = list(data["month_name"].unique())
        show_month = st.sidebar.multiselect(
            "Select **Months** to Display",
            options=select_month,
            default=[
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
        )
        st.sidebar.divider()
        print_df = st.sidebar.toggle(label="View Dataframe")

        filtered_data = data[
            (data["custom_category"].isin(selected_categories))
            & (data["year"].isin(show_year) & (data["month_name"].isin(show_month)))
        ]

        total_spend = filtered_data["Amount"].sum().round(2)

        cat_amount_df = return_cat_amount_df(filtered_data)
        name_amount_df = return_name_amount_df(filtered_data)
        cat_amount_date_df_week = return_cat_amount_date_df(filtered_data, period="W")
        cat_amount_date_df_mth = return_cat_amount_date_df(filtered_data, period="M")
        cat_amount_date_df_year = return_cat_amount_date_df(filtered_data, period="Y")

        st.metric(label="Total Spend", value="£ " + str(total_spend))

        c1, c2 = st.columns(2)

        with c1:
            chart_cat = (
                alt.Chart(cat_amount_df)
                .mark_arc(innerRadius=60)
                .encode(
                    theta="Amount",
                    color="custom_category:N",
                )
            )
            # Display the chart in Streamlit
            st.altair_chart(chart_cat, use_container_width=True, theme="streamlit")

        with c2:
            chart_name = (
                alt.Chart(name_amount_df)
                .mark_arc(innerRadius=60)
                .encode(
                    theta="Amount",
                    color="Name:N",
                )
            )
            # Display the chart in Streamlit
            st.altair_chart(chart_name, use_container_width=True, theme="streamlit")

        st.subheader("Week")
        line_week = (
            alt.Chart(cat_amount_date_df_week)
            .mark_line(interpolate="monotone")
            .encode(x="Date:T", y="Amount:Q", color="custom_category:N")
        )
        st.altair_chart(line_week, use_container_width=True, theme="streamlit")

        st.subheader("Month")
        line_mth = (
            alt.Chart(cat_amount_date_df_mth)
            .mark_line(interpolate="monotone", point=True)
            .encode(
                x=alt.X("Date:T", axis=alt.Axis(grid=True)),
                y=alt.Y("Amount:Q", axis=alt.Axis(grid=True)),
                color="custom_category:N",
            )
        )
        st.altair_chart(line_mth, use_container_width=True, theme="streamlit")
        st.subheader("Year")
        line_year = (
            alt.Chart(cat_amount_date_df_year)
            .mark_line(interpolate="monotone", point=True)
            .encode(x="Date:T", y="Amount:Q", color="custom_category:N")
        )
        st.altair_chart(line_year, use_container_width=True, theme="streamlit")

        if print_df == True:
            st.divider()
            st.dataframe(cat_amount_date_df_mth)

    elif tabs == "View | Update - Budget":
        st.header("Budget Documents")
        with st.expander(label="Budget - DataFrame", icon=":material/savings:"):
            st.dataframe(budget)

        with st.expander(
            label="Budget prepped with Statement Info - DataFrame",
            icon=":material/savings:",
        ):
            st.dataframe(current)

        with st.expander(label="Budget - Google Sheet", icon=":material/savings:"):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?gid=1571834654#gid=1571834654"
            st.components.v1.html(
                f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>',
                height=600,
            )

    elif tabs == "View | Update - Bank Statement":
        st.header("Bank Statements")
        with st.expander(
            label="Account Statement - DataFrame", icon=":material/credit_card:"
        ):
            st.dataframe(data)

        with st.expander(
            label="Account Statement for Budget - DataFrame",
            icon=":material/credit_card:",
        ):
            st.dataframe(filtered_bank_statement)

        with st.expander(
            label="Account Statement - Google Sheet", icon=":material/credit_card:"
        ):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?usp=sharing"
            st.components.v1.html(
                f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>',
                height=600,
            )

    elif tabs == "Settings":
        st.header("Settings")
