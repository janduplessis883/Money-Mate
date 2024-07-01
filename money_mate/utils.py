import time
from loguru import logger
import pandas as pd
from datetime import datetime, timedelta

# = Decorators =========================================================================================================

def time_it(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"🖥️    Started: '{func_name}'")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        func_name = func.__name__
        logger.info(f"✅ Completed: '{func_name}' ⚡️{elapsed_time:.6f} sec")
        return result

    return wrapper




# Universal functions ==================================================================================================
mapping = {
    "Stuff": [
        "Amazon",
        "Amazon Music",
        "Audible",
        "Clonezone",
        "Clonezone - Soho",
        "G-star Raw",
        "GSingh",
        "IKEA",
        "Leyland Lsdm Earl's Court",
        "Leyland SDM",
        "Robert Dyas",
        "United Shop Company",
        "eBay",
        "www.thickwall.co.uk",
        "World Duty Free",
        "Apple Store",
    ],
    "Travel": [
        "TIER",
        "Tier Mobility",
        "Sendwave",
        "Zipcar",
        "Tier Mobility",
        "Lime",
        "Transport for London",
        "CMT UK Taxi Fare",
        "Uber",
        "Easi Rent",
        "easirent",
        "London Taxi",
    ],
    "Subscriptions": [
        "Wordtune",
        "Automate.io",
        "Coursera",
        "Rytr - Ai Writer",
        "Netflix",
        "Zapier",
        "Notion2shee",
        "Nutt Labs + Notion Vip",
        "Google",
        "Yourdataltd",
        "Airtable.com/bill",
        "Pipedream, Inc.",
        "Superhuman",
        "Fs Revoicer",
        "Heroku",
        "Deep Learning Courses",
        "Render.com",
        "Setapp",
        "Spark",
        "Motion ",
        "Browserless",
        "www.make.com",
        "Claude",
        "WOW Presents PLUS",
        "Microsoft",
        "Loom Subscription",
        "AmazPrimeSubs",
        "Super Publishing Co.",
        "Apple",
        "Perplexity",
        "Notion",
        "OpenAI",
        "Monzo Premium",
        "Anthropic",
        "Motion -1 Temp Hold",
        "Brompton Super",
        "ExpressVPN",
        "Grammarly",
        "Granity-ent.com",
        "Heart Internet",
        "Jarvis - Conversion.ai",
        "Realpython",
        "Surfshark",
        "PureGym",
    ],
    "Groceries": [
        "Jms Food Store",
        "J M S Foods",
        "Sunfield Foods",
        "Amazon Fresh",
        "Lidl",
        "Waitrose & Partners",
        "M&S",
        "Tesco",
        "London Taxi 77619",
        "Sainsbury’s",
        "Co-op",
        "Deepak Self Service",
        "Chelsea Food Fayre",
        "Chelsea Food Worldsend",
        "Cumberland Food & Wine",
        "Earls Court Food And Wine",
        "J M S Food & News",
        "My Shop",
        "On The Go",
        "Chelsea Food And Wine",
    ],
    "Eating-Out": [
        "Taco Bell",
        "Paul Uk Hammersmith",
        "John Forrest Master Ba",
        "Five Guys",
        "Mona Lisa Cafe",
        "Wagamama",
        "Balans West",
        "Ollie’s House Limited",
        "The Monument",
        "Pret",
        "Nando’s",
        "The Grove Tavern",
        "Yoco Pickled Green",
        "Star Wraps",
        "Bagel Bakery Bar",
        "Greggs",
        "PAUL Earls Court",
        "Lions Prep",
        "Patri Takeaway",
        "Deliveroo",
        "Leon",
        "Black Rabbit Cafe",
        "GAIL's Bakery",
        "McDonald’s",
        "Starbucks",
        "Buff Meat",
        "Burger King",
        "Domino’s",
        "KFC",
        "Masala",
        "PAUL Hammersmith",
        "Pho",
        "The Bull Westfield",
        "The Grove",
        "Too Good To Go",
        "Coffee",
        "The Swan",
        "Bayswater Arms",
        "Soft Ice",
        "Old Ship, Hammersmith",
        "Riverside Studio",
    ],
    "Telephone": [
        "Airalo",
        "TELSERVE LIMITED",
        "EE",
        "plan.com",
        "giffgaff",
    ],
    "Rent": ["Hampton Management", "Hampton Rent"],
    "Smoking": [
        "On The Goo",
        "The Smoking Jacket",
        "Cheyne News",
        "Deepak Self Service",
        "Lucky Me Enterprise",
        "smoking",
    ],
    "Debt-Payment": [
        "Credit Resource Solutions",
        "Flex",
    ],
    "Medical": [
        "Medicine Chest",
        "Boots",
        "NHS Prescription Prepayment",
        "Green Light Pharmacy",
        "Earls Court Chemist",
        "Superdrug",
        "Zafash Pharmacy",
    ],
    "Other": [
        "James Vokins",
        "Empriel",
        "PayPal",
        "Rm Media",
        "Leatherpr",
        "Michele Manzolillo",
        "Dipanno Dario",
        "Jan Du plessis revolut",
        "Alessandro Dei Agnoli",
        "Skrill9959",
        "James Vockins",
        "kucoin.com",
        "Patreon",
        "Cash App",
        "Wishtender.com",
        "Skrill3395",
        "Coinbase Payments",
        "Coinbase",
        "ATM",
        "carlos",
        "Kostadin Milchev",
        "Revolut",
        "coinbase",
        "Koronapay Europe",
        "A Garcia",
        "Cornelioallanj",
    ],
    "Credit Cards": [
        "Capital One",
        "Vanquis Bank",
    ],
    "Income": [
        "GOOD RESEARCH LTD",
        "DR BURHAN ALI ADIB AND DR ORIETTA E",
        "DU PLESSIS J V B",
        "- GOOD RESEARCH LT",
        "EARLS CT SUR",
        "Atlantic Medical",
        "TWL Cattle Farming",
    ],
    "Savings + Transfer": [
        "LE-TELLIER J",
        "Jan du Plessis",
        "50p Savings Pot",
        "Jan Van-Breda-Du-P",
        "Jean-Pierre LE TELLIER",
        "Complete Savings",
        "Plum",
    ],
    "Holiday": [
        "Airbnb",
        "Booking.com",
        "Bootlegger Cape Quarte",
        "The Grey Hotel",
        "Wise Holiday",
        "Woodford Car Hire",
    ],
    "Barber": [
        "Sw5 Barbers Lt",
        "Cut And Go",
        "Old Brompton Barbers",
    ],
    "Bank Charges": [
        "Bank Charges",
    ],
    "South-Africa": [
        "Julie Young",
        "Thom",
        "Myra Cosio",
    ],
    "Tax":
        ["HMRC",]
}

def categorize(name):
    if isinstance(name, str):
        name = name.lower()
        for category, names in mapping.items():
            for n in names:
                if n.lower() in name:
                    return category
    return "Uncategorized"


def prep_account_statement(df):
    df.drop(columns=["Transaction ID", "Category split", "Receipt"], inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month

    df["categories"] = df["Name"].apply(categorize)
    df["Cumulative Amount"] = df["Amount"].cumsum().round(2)

    return df

def prep_budget(df):
    budget = df.groupby(by="Category")["Amount"].sum().reset_index()
    budget.columns = ["categories", "Budget"]

    return budget


def prep_statement_import_to_budget(df):
    # Convert the 'date' column to datetime if it isn't already
    df["Date"] = pd.to_datetime(df["Date"])

    # Get the current date
    current_date = datetime.now()

    # Calculate the start date for tracking (24th of the previous month)
    if current_date.day >= 24:
        start_date = current_date.replace(day=24)
    else:
        # If the current day is less than 24, go to the previous month
        start_date = (current_date - pd.DateOffset(months=1)).replace(day=24)

    # Filter the dfFrame to get rows from the start date onwards
    filtered_bank_statement = df[df["Date"] >= start_date]


    # Calculate the number of days remaining until the 24th of the current month
    next_24th = current_date.replace(day=25)
    if current_date.day > 25:
        next_24th = (current_date + pd.DateOffset(months=1)).replace(day=24)
    days_remaining = (next_24th - current_date).days

    return filtered_bank_statement, days_remaining


def generate_budget_df(filtered_bank_statement, budget):
    current_expenses_by_cat = filtered_bank_statement.groupby(by='categories')['Amount'].sum().abs().reset_index()
    current = budget.merge(current_expenses_by_cat, how='left', on='categories').fillna(0)
    current['Diff'] =  current['Budget'] - current['Amount']

    return current


def budget_df_min_income(current):
    current_minus_income = current[current["categories"] != "Income"]

    return current_minus_income


def prep_budget_metrics(current, days_remaining):
    total_budget = abs(current['Budget'].sum().round(2))
    income_value = abs(current.loc[current["categories"] == "Income", "Diff"].values[0])
    current_minus_income = budget_df_min_income(current)
    budget_used_sum = current_minus_income["Amount"].sum().round(2)
    remaining_budget = current_minus_income["Diff"].sum().round(2)
    over_spent = (
        current_minus_income[current_minus_income["Diff"] < 0]["Diff"].sum().round(2)
    )
    daily_budget = (remaining_budget / days_remaining).round(2)

    projected_disposable_income = (income_value - total_budget).round(2)
    actual_disposable_income = ((income_value - total_budget) - abs(over_spent)).round(2)

    return total_budget, income_value, budget_used_sum, over_spent, remaining_budget, daily_budget, projected_disposable_income, actual_disposable_income


def return_cat_amount_df(filtered_data):
    cat_amount_df = filtered_data.groupby('categories').agg({'Amount': 'sum'}).reset_index()

    return cat_amount_df

def return_name_amount_df(filtered_data):
    name_amount_df = filtered_data.groupby('Name').agg({'Amount': 'sum'}).reset_index()

    return name_amount_df

def return_cat_amount_date_df(filtered_data, period="W"):
    filtered_data = filtered_data.set_index('Date')
    # Group by 'categories' and resample within each group, then aggregate 'Amount'
    cat_amount_date_df = filtered_data.groupby('categories').resample(period).agg({'Amount': 'sum'}).reset_index()

    return cat_amount_date_df
