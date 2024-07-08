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
import toml

from utils import *
from classification import *

# Load Setting via settings.toml file
def load_settings(file_path="settings.toml"):
    with open(file_path, "r") as file:
        settings = toml.load(file)
    return settings

def save_settings(settings, file_path="settings.toml"):
    with open(file_path, "w") as file:
        toml.dump(settings, file)

settings = load_settings()

# Access settings
app_version = settings['general']['version']

smoke_min_value = settings['smoking_price_range']['smoke_min']
smoke_max_value = settings['smoking_price_range']['smoke_max']

rent_value = settings['budget']['rent']
tax_value = settings['budget']['tax']
credit_cards_value = settings['budget']['credit_cards']
telephone_value = settings['budget']['telephone']
bank_charges_value = settings['budget']['bank_charges']
medical_value = settings['budget']['medical']
barber_value = settings['budget']['barber']
eating_out_value = settings['budget']['eating_out']
groceries_value = settings['budget']['groceries']
holiday_value = settings['budget']['holiday']
loan_value = settings['budget']['loan']
other_value = settings['budget']['other']
transport_value = settings['budget']['transport']
shopping_value = settings['budget']['shopping']
smoking_value = settings['budget']['smoking']
subscriptions_value = settings['budget']['subscriptions']
sa_investment_value = settings['budget']['sa_investment']
uncategorized_value = settings['budget']['uncategorized']
income_amount = settings['salary']['income']
# End of Settings --------------------------------------------------------------

# Set the page configuration to have a wide layout and the sidebar collapsed on load
st.set_page_config(
    layout="wide", initial_sidebar_state="collapsed", page_title="Money-Mate", page_icon=":material/savings:"
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
    st.markdown("# ![Money-Mate](https://img.icons8.com/ios/50/coins--v1.png) Money-Mate")
    ui.badges(badge_list=[(f"version {app_version}", "outline")], class_name="flex gap-2", key="version_badge")

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
            "Budget Calculations",
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
    budget_data = {
        "Budget Category": ["Rent", "Tax", "Credit Cards", "Telephone", "Bank Charges", "Medical", "Transport", "Subscriptions", "Barber", "Eating Out", "Groceries", "Holiday", "Loan", "Other", "Shopping", "Smoking", "SA Investment", "Uncategorized"],
        "Budget Amount": [rent_value, tax_value, credit_cards_value, telephone_value, bank_charges_value, medical_value, transport_value, subscriptions_value, barber_value, eating_out_value, groceries_value, holiday_value, loan_value, other_value, shopping_value, smoking_value, sa_investment_value, uncategorized_value],
    }
    regular_expenses = pd.DataFrame(budget_data)


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
        budget_used_sum,
        over_spent,
        remaining_budget,
        daily_allowance,
        projected_disposable_income,
        actual_disposable_income,
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
            f"""**Daily Allowance**: £ {daily_allowance}""",
            icon=":material/light_mode:",
        )

    if tabs == "Account Summary":
        st.header("Account Summary")

        st.metric("Monzo Account Balance", value="£ " + str(account_balance))

        c1, c2 = st.columns(2)
        with c1:
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

        with c2:
            st.write("")
            st.write("")
            st.write("")
            st.dataframe(filtered_bank_statement.tail(7))

    elif tabs == "Budget":
        st.header("Budget")
        st.sidebar.divider()
        # Streamlit slider
        st.sidebar.header("Budget and Expense Tracker")
        st.sidebar.write("Adjust your variable expenses using the slider below:")
        variable_expenses_slider = st.sidebar.slider(
            "Variable Expenses",
            min_value=0,
            max_value=int(variable_expenses),
            value=int(variable_expenses) // 2,
        )

        st.sidebar.markdown(
            f"You have selected **£ {variable_expenses_slider}** for your variable expenses."
        )


        # Use the slider value in your application
        # For example, update remaining budget based on slider value
        remaining_budget_adjusted = remaining_budget - variable_expenses_slider
        adjusted_remaining_budget = remaining_budget - (
            variable_expenses - variable_expenses_slider
        )
        adjusted_daily_allowance = (
            (adjusted_remaining_budget / days_remaining).round(2)
            if days_remaining
            else 0
        )
        st.sidebar.markdown(
            f"Adjusted remaining budget: **£ {remaining_budget_adjusted.round(2)}**"
        )
        st.sidebar.markdown(
            f"Adjusted daily allowance: **£ {adjusted_daily_allowance}**"
        )
        st.sidebar.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="Total Monthly Budget", value="£ " + str(total_budget))
        c2.metric(label="Remaining Budget", value="£ " + str(remaining_budget))
        c3.metric(label="Over-spent", value="£ " + str(over_spent))
        c4.metric(
            label="Total Spending this month.",
            value="£ " + str(total_budget + over_spent),
        )

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
            .mark_point(color="#bb271a", size=80)
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
        c1.metric(label="INCOME", value="£ " + str(income_amount))
        c2.metric(label="Remaining this Month", value="£ " + str((income_amount - (total_budget + over_spent)).round(2)))
        c3.metric(label="Fixed Expenses", value="£ " + str(calculate_fixed_expenses(current)))
        c4.metric(
            label="Days till next Paydat", value=str(days_remaining)+" days"
        )

        st.markdown(f"**:blue[Income]** minus **:red[Fixed Expenses]** = **£ {(income_amount - calculate_fixed_expenses(current)).round(2)}**")
        st.markdown(f"**:green[Variable Expenses]** £ {(calculate_variable_expenses(current)).round(2)} plus **:red[Fixed Expenses]** = **£ {(calculate_variable_expenses(current) + calculate_fixed_expenses(current)).round(2)}**")
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
        select_list = list(data["custom_category"].unique())
        selected_categories = st.sidebar.multiselect(
            "Select **Categories** to Display",
            options=select_list,
            default=select_list,
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

    elif tabs == "Budget Calculations":
        st.header("Budget Calculations")

        with st.expander("**Fixed Expenses** - calculation", icon=":material/calculate:"):
            st.markdown(
                f"Salary: **£ {income_amount}** - Budget: **£ {total_budget}** = Left-over: **£ {projected_disposable_income}**"
            )
            st.markdown(
                f":blue[**Variable Expenses**: (Barber, Eating Out, Groceries, Holiday, Shopping, Smoking, Transport): **£ {variable_expenses}**] - :red[over-spent: **£ {over_spent}**] = **£ {(variable_expenses - over_spent).round(2)}**"
            )
            st.markdown(f":red[Daily Allovance: **£ {daily_allowance}**]")


    elif tabs == "Settings":
        st.header("Settings")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("General Settings")

            version = st.text_input("Version", settings['general']['version'])

            smoke_min, smoke_max = st.slider(
                label="Select a range",
                min_value=10.00,
                max_value=20.00,
                value=(smoke_min_value, smoke_max_value),
                step=0.05,
                format="%.2f"
            )

            # Display the selected values
            st.write(f"Selected range: {smoke_min} to {smoke_max}")

            st.subheader("Income")
            income = st.number_input("Enter Salary / Income for the month.", value=income_amount)
            # Create sliders for each category
            st.subheader("Budget Settings (Fixed Expenses)")
            rent = st.slider("Set budget for **Rent**", 0, 1500, rent_value)
            tax = st.slider("Set budget for **Tax**", 0, 300, tax_value)
            credit_cards = st.slider("Set budget for **Credit Cards**", 0, 4000, credit_cards_value)
            telephone = st.slider("Set budget for **Telephone**", 0, 400, telephone_value)
            bank_charges = st.slider("Set budget for **Bank Charges**", 0, 50, bank_charges_value)
            medical = st.slider("Set budget for **Medical**", 0, 50, medical_value)
            transport = st.slider("Set budget for **Transport**", 0, 100, transport_value)

            st.subheader("Budget Settings (Variable Expenses)")
            subscriptions = st.slider("Set budget for **Subscriptions**", 0, 200, subscriptions_value)
            barber = st.slider("Set budget for **Barber**", 0, 70, barber_value)
            eating_out = st.slider("Set budget for **Eating Out**", 0, 500, eating_out_value)
            groceries = st.slider("Set budget for **Groceries**", 0, 500, groceries_value)
            holiday = st.slider("Set budget for **Holiday**", 0, 5000, holiday_value)
            loan = st.slider("Set budget for **Loan**", 0, 200, loan_value)
            other = st.slider("Set budget for **Other**", 0, 1000, other_value)
            shopping = st.slider("Set budget for **Shopping**", 0, 400, shopping_value)
            smoking = st.slider("Set budget for **Smoking**", 0, 400, smoking_value)
            sa_investment = st.slider("Set budget for **SA Investment**", 0, 3000, sa_investment_value)
            uncategorized = st.slider("Set budget for **Uncategorized**", 0, 3000, uncategorized_value)


            # Calculate the total budget
            total_budget = (
                rent + tax + credit_cards + telephone + bank_charges + medical + barber +
                eating_out + groceries + holiday + loan + other + transport + shopping +
                smoking + subscriptions + sa_investment + uncategorized
            )

            if st.button("Save Settings"):
                settings['general']['version'] = version
                settings['smoking_price_range']['smoke_min'] = smoke_min
                settings['smoking_price_range']['smoke_max'] = smoke_max

                settings['budget']['rent'] = rent
                settings['budget']['tax'] = tax
                settings['budget']['credit_cards'] = credit_cards
                settings['budget']['telephone'] = telephone
                settings['budget']['bank_charges'] = bank_charges
                settings['budget']['medical'] = medical
                settings['budget']['barber'] = barber
                settings['budget']['eating_out'] = eating_out
                settings['budget']['groceries'] = groceries
                settings['budget']['holiday'] = holiday
                settings['budget']['loan'] = loan
                settings['budget']['other'] = other
                settings['budget']['transport'] = transport
                settings['budget']['shopping'] = shopping
                settings['budget']['smoking'] = smoking
                settings['budget']['subscriptions'] = subscriptions
                settings['budget']['sa_investment'] = sa_investment
                settings['budget']['uncategorized'] = uncategorized

                settings['salary']['income'] = income

                save_settings(settings)
                st.success("Settings updated successfully!")

            st.markdown(f"### Total Budget: **{total_budget}**")

        with col2:
            pass
        # Display updated settings
        st.write("Current Settings:")
        st.write(settings)
