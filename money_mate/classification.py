import pandas as pd
from datetime import datetime, timedelta
import toml

# Load Setting via settings.toml file
def load_settings(file_path="settings.toml"):
    with open(file_path, "r") as file:
        settings = toml.load(file)
    return settings

settings = load_settings()

# Access settings
app_version = settings['general']['version']

smoke_min_value = settings['smoking_price_range']['smoke_min']
smoke_max_value = settings['smoking_price_range']['smoke_max']

income_amount = settings['salary']['income']
pay_date_value = settings['salary']['pay_date']

transaction_type_rules = {
    "wise_cashback": "Income",
    "Pot transfer": "Transfer",
    "overdraft": "Bank Charges",
    "Monzo Paid": "Bank Charges",
    "Flex": "Loan",
    "Account interest": "Income",
    "Bacs (Direct Credit)": "Income",
}

transaction_name_rules = {
    "Shopping": [
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
        "Futon Ltd",
    ],
    "Eating Out": [
        "Riverside Studios",
        "Masala",
        "Pix Pintxo Bateman",
        "Kula",
        "Nando’s",
        "SOHO Coffee Co.",
        "Soft Ice",
        "Too Good To Go",
        "Cafe Manhattans",
        "Paul Uk Gloucester Rd",
        "Old Ship, Hammersmith",
        "Black Rabbit Cafe",
        "PAUL Hammersmith",
        "Da Bagel Spot",
        "Bertotti Pure Italian",
        "La Pappardella",
        "Kucci Cafe",
        "Comptoir Libanais",
        "Wondertree",
        "Alamo Spur        3415",
        "Pret",
        "Napier Farmstall  3836",
        "Pizza Home West Brompt",
        "Maoz",
        "Bayswater Arms",
        "Chalet Cafe",
        "Comptons London",
        "Maroush Bakehouse",
        "Lions Prep",
        "The Bolton",
        "Blanche Eatery Kensing",
        "Star Pizza",
        "Audrey Green",
        "Peregrine Farm Stall",
        "Taco Bell",
        "Wahaca",
        "Yoco Pickled Green",
        "Chalet",
        "Tesco Petrol",
        "Hooked Fish Bar",
        "Marias Fish Bar",
        "Ik Infusion Social Cl",
        "V&A Food Market",
        "North Lodge Cafe",
        "Bagel Bakery Bar",
        "GAIL's Bakery",
        "Masala Zone Earls Cour",
        "MEATliquor",
        "Paul",
        "Juicebaby Ltd",
        "Gordon Ramsay Street Burger",
        "Hasty Tasty Pizza",
        "Black Sheep Coffee",
        "Creams Kings Cross Lon",
        "Mcd Seapoint (0465)",
        "Star Wraps",
        "Tapas Revoluti",
        "Mad Paella Ltd.",
        "Big Bite",
        "Crosstown",
        "Shawa Westfield",
        "Costa Coffee",
        "Delhi By Nature Ltd",
        "Burger King",
        "Busaba",
        "Raitakrai",
        "Casa Manolo",
        "Aeroporto de Lisboa",
        "Starbucks",
        "Indi-go Rasoi",
        "The Bull Westfield",
        "Balans Westfield Londo\\unit 1034\\lo",
        "Patri Takeaway",
        "Coffee&cates",
        "Cafe Du Coin",
        "Wok to Walk",
        "Cafe Boheme",
        "Subway",
        "Kings Arms",
        "Pure",
        "Peregrine Farm St26542",
        "The Gallery",
        "Battersea Park Cafe Gr",
        "Emirates Leis Concd Dr",
        "Snackers",
        "KFC",
        "Stella Coffee",
        "Lillie Langtry Fulham",
        "Kings Kebab Hous",
        "The Prince of Teck",
        "McDonald’s",
        "Rwrd Ltd",
        "Fresh Bake",
        "Mona Lisa Cafe",
        "Lamb Rolla",
        "Ibericos",
        "Il Molino",
        "Over Under : West Brom",
        "Mad Paella",
        "Hawker Bar",
        "Pho",
        "Ichiba",
        "Five Guys",
        "Panopolis",
        "PAUL Earls Court",
        "John Forrest Master Ba",
        "Prince Of Teck, Earls",
        "Cleopatra Restaurant",
        "Padaria Lisboa",
        "Wagamama",
        "You Me Sushi Ec",
        "Deliveroo",
        "The Swan",
        "BrewDog",
        "The Monument",
        "Paul Uk Hammersmith",
        "Central Station",
        "Bloomsbury Theatre Bar",
        "Kipps",
        "Joe & The Juice Uk Ltd",
        "Alma Cafe Ltd",
        "Prince Regent",
        "Balans West",
        "Go Go Gourmet Pizza",
        "Organicos Coffee",
        "Fresh Healty Foods Ltd",
        "Riverside Studio",
        "Cofx",
        "Swallow Coffee Shop",
        "Greggs",
        "Domino’s",
        "The Grove",
        "Coffee",
        "Amoret Coffee",
        "Johnnie's Fish Bar",
        "Samosa Haus",
        "Buff Meat",
        "Charco's",
        "Belushis Hammersmith",
        "The William Morris",
        "Leon",
        "Elgin Purepere",
        "Eat17",
        "Emirates Leis Dxbt1 Ar",
        "Bagel Bite",
        "Wasabi",
        "Sky Bar",
        "Londontaxiltd",
        "The Hoarder",
        "Caffè Nero",
        "Organicos Coffee &",
        "Yole Covent Garden",
        "The Grove Tavern",
        "Lebanese Taverna",
        "Ollie’s House Limited",
        "The Plough & Harrow",
        "Segar & Snuff Parl",
        "Popeyes",
    ],
    "Transport": [
        "Sendwave",
        "Zipcar",
        "Tier Mobility",
        "Lime",
        "Transport for London",
        "CMT UK Taxi Fare",
        "Uber",
        "Easi Rent",
        "easirent",
        "TIER",
        "Lime Ride Welp",
        "Lime Auth Welp",
        "Lime Pass Welp",
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
        "Amazon Prime",
        "Super Publishing Co.",
        "Apple",
        "Perplexity",
        "Notion",
        "OpenAI",
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
        "Macpaw",
        "Codegate",
        "Artemisa 3000",
        "Blaze Today",
        "Buymeacoffee.com",
        "Finalprice.club",
        "Grammarly Coqvuzrki",
        "Gyrosco Pe App",
        "Jasper.ai (ex. Jarvis)",
        "Kucoin",
        "LimeBike",
        "Notion-automations.com",
        "Pluralsight",
        "Rapidapi",
        "Semrush.com",
        "Stewardware 1888 600 7",
        "Trial Over",
        "Vimeo",
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
    "Telephone": [
        "Airalo",
        "TELSERVE LIMITED",
        "EE",
        "plan.com",
        "giffgaff",
        "Three",
        "Invoice 240724538588",
    ],
    "Loan": [
        "Credit Resource Solutions",
    ],
    "Medical": [
        "Medicine Chest",
        "Boots",
        "NHS Prescription Prepayment",
        "Green Light Pharmacy",
        "Earls Court Chemist",
        "Superdrug",
        "Zafash Pharmacy",
        "Londonskin&hairclinic",
        "24/7 Zafash Pharmacy",
        "Jhoots Pharmacy",
        "Hammersmith Pharmacy",
        "Nhsbsa Ppc 2",
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
        "ATM",
        "carlos",
        "Kostadin Milchev",
        "Revolut",
        "Koronapay Europe",
        "A Garcia",
        "Cornelioallanj",
        "Carlos",
        "Alesya Zhilenkova",
        "Koronapay Europe",
        "Revolut",
        "Anewskincar",
    ],
    "Credit Cards": [
        "Capital One",
        "Vanquis Bank",
    ],
    "Gift": [
        "Jules Young",
        "Myra Cosio",
        "Jean-Pierre LE TELLIER",
        "Jean-Pierre Le Tillier",
        "Julie Young",
    ],
    "Holiday": [
        "Airbnb",
        "Booking.com",
        "Bootlegger Cape Quarte",
        "The Grey Hotel",
        "Wise Holiday",
        "Woodford Car Hire",
        "ShopRite",
        "Costa Coffee",
        "Premium Computers 4112",
        "Retail Outlet",
        "Sorbet Man Cape Quarte",
        "V&A Food Market",
        "The Grey Hotel",
        "Klein River Cheese (pt",
        "Ik Mother City Liquor",
        "Peregrine Farm Stall",
        "Cafe Manhattans",
        "Interpark The Point",
        "Tops Cape Quarter 1",
        "BP",
        "Ae Napier",
        "Woodford Car Hire",
        "L A E Sea Point",
        "City Sightseeing Sa",
        "V&A Waterfront",
        "Mcd Seapoint (0465)",
        "Clicks Cape Quarter",
        "Clicks Regent Road",
        "Icons",
        "Peregrine Farm St26542",
        "Yoco Pickled Green",
        "Napier Farmstall  3836",
        "ATM",
        "Lamb Rolla",
        "The Capital Mirage",
        "Big Five Duty Free",
        "Scz",
        "Alamo Spur        3415",
        "Spar",
        "Elgin Purepere",
        "Overberg Agri Napier O",
        "Time Out Market Cape Town",
        "Rola Ford Caledon",
        "Ik Infusion Social Cl",
        "Sea Point Tobac  12236",
        "Bootlegger Cape Quarte",
        "Cancom",
        "Nelson Mandela",
        "H&M",
    ],
    "Barber": [
        "Sw5 Barbers Lt",
        "Cut And Go",
        "Old Brompton Barbers",
        "Barber",
    ],
    "SA Investment": [
        "Thom",
    ],
    "Tax": [
        "HMRC",
    ],
    "Transfer": [
        "TWL Cattle Farming",
        "Plum",
        "Capital One Mobile App",
        "Jan Du Plessis Virgin Online Current",
        "Wise Transfer",
        "Igor Lokmanis",
        "Jean-Pierre Virgin 2",
        "Jan Du Plessis Barclays",
    ],
    "Rent": ["Hampton Management", "Hampton Rent", "Electricity"],
    "Smoking": [
        "On The Goo",
        "The Smoking Jacket",
        "Cheyne News",
        "Deepak Self Service",
        "Lucky Me Enterprise",
        "Smoking",
        "Evapo",
        "Vapourcore Earls Court",
        "UPS",
        "Days &nights L",
        "Day And Night Convenience",
    ],
    "Income": [
        "GOOD RESEARCH LTD",
        "DR BURHAN ALI ADIB AND DR ORIETTA E",
        "DU PLESSIS J V B",
        "- GOOD RESEARCH LT",
        "- GOOD RESEARCH LTD",
        "EARLS CT SUR",
        "Atlantic Medical",
        "LONDON MEDICAL ASSOCIATES LTD",
        "Tide Business Account",
    ],
}

startswith_rules = {
    "Transport": [
        "London Taxi",
        "Tier",
        "Taxi",
        "Uber",
        "Zipcar",
        "Lime",
    ],
    "Eating Out": [
        "Toogoodt",
    ],
    "Other": ["Leather", "Coinbase"],
    "Subscription": [
        "Grammerly",
    ],
    "Smoking": [
        "Krystals",
        "United Shop Company",
    ],
    "Holiday": [
        "Hotel Cascais",
    ],
}


# Define functions for classification
def classify_by_type(row):
    return transaction_type_rules.get(row["Type"], "Uncategorized")


def classify_by_name(row, startswith_rules):
    for category, prefixes in startswith_rules.items():
        for prefix in prefixes:
            if row["Name"].startswith(prefix):
                return category
    return None


def refine_by_name(row):
    category = classify_by_name(row, startswith_rules)
    if category:
        return category

    if (
        row["custom_category"] == "Uncategorized"
        or row["custom_category"] in transaction_name_rules
    ):
        for category, names in transaction_name_rules.items():
            if row["Name"] in names:
                return category
    return row["custom_category"]

# "Local amount", "Local currency", "Notes and #tags", "Address", "Description"
def prep_account_statement(df):
    df.drop(
        columns=[
            "Transaction ID",
            "Category split",
            "Receipt",
            "Address",
            "Description",
            "Notes and #tags",
        ],
        inplace=True,
    )
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["month_name"] = df["Date"].dt.strftime("%b")

    df["Name"] = df["Name"].fillna("")
    df["custom_category"] = df.apply(classify_by_type, axis=1)
    df["custom_category"] = df.apply(refine_by_name, axis=1)
    df["Cumulative Amount"] = df["Amount"].cumsum().round(2)
    return df

def get_account_balance(df):
    account_balance = df["Cumulative Amount"].iloc[-1]
    return account_balance

def prep_budget(df):
    budget = df.groupby(by="Budget Category")["Budget Amount"].sum().reset_index()
    budget.columns = ["custom_category", "Budget"]
    return budget

def prep_statement_import_to_budget(df):
    df["Date"] = pd.to_datetime(df["Date"])
    current_date = datetime.now()

    if current_date.day >= pay_date_value:
        start_date = current_date.replace(day=pay_date_value)
    else:
        start_date = (current_date - pd.DateOffset(months=1)).replace(day=pay_date_value)

    filtered_bank_statement = df[df["Date"] >= start_date]
    next_pay_date = start_date + pd.DateOffset(months=1)
    days_remaining = (next_pay_date - current_date).days

    return filtered_bank_statement, days_remaining

def generate_budget_df(filtered_bank_statement, budget):
    current_expenses_by_cat = (
        filtered_bank_statement.groupby(by="custom_category")["Amount"]
        .sum()
        .abs()
        .reset_index()
    )
    current = budget.merge(
        current_expenses_by_cat, how="left", on="custom_category"
    ).fillna(0)
    current["Diff"] = current["Budget"] - current["Amount"]

    return current

def budget_df_min_income(current):
    current_minus_income = current[
        (
            (current["custom_category"] != "Income")
            & (current["custom_category"] != "Rent")
        )
    ]
    return current_minus_income

def calculate_variable_expenses(current):
    variable_expenses_df = current[
        (
            (current["custom_category"] == "Barber")
            | (current["custom_category"] == "Eating Out")
            | (current["custom_category"] == "Groceries")
            | (current["custom_category"] == "Holiday")
            | (current["custom_category"] == "Shopping")
            | (current["custom_category"] == "Smoking")
            | (current["custom_category"] == "Transport")
            | (current["custom_category"] == "Other")
        )
    ]
    variable_expenses = variable_expenses_df["Budget"].sum()

    return variable_expenses.round(2)

def calculate_fixed_expenses(current):
    fixed_expenses_df = current[
        (
            (current["custom_category"] == "Rent")
            | (current["custom_category"] == "Loan")
            | (current["custom_category"] == "Tax")
            | (current["custom_category"] == "Telephone")
            | (current["custom_category"] == "Credit Cards")
            | (current["custom_category"] == "Bank Charges")
            | (current["custom_category"] == "Medical")
        )
    ]
    fixed_expenses = fixed_expenses_df["Budget"].sum()

    return fixed_expenses.round(2)

def prep_budget_metrics(current, days_remaining):
    total_budget = abs(current["Budget"].sum().round(2))
    variable_expenses = calculate_variable_expenses(current)
    current_minus_income = budget_df_min_income(current)
    budget_used_sum = current_minus_income["Amount"].sum().round(2)
    remaining_budget = abs(
        current_minus_income[current_minus_income["Diff"] > 0]["Diff"].sum().round(2)
    )
    over_spent = abs(
        current_minus_income[current_minus_income["Diff"] < 0]["Diff"].sum().round(2)
    )
    over_spent = abs(over_spent)

    daily_allowance = (
        (calculate_variable_expenses(current) / days_remaining).round(2)
        if days_remaining
        else 0
    )

    projected_disposable_income = (income_amount - total_budget).round(2)
    actual_disposable_income = ((income_amount - total_budget) - abs(over_spent)).round(
        2
    )

    return (
        variable_expenses,
        total_budget,
        budget_used_sum,
        over_spent,
        remaining_budget,
        daily_allowance,
        projected_disposable_income,
        actual_disposable_income,
    )

def return_cat_amount_df(filtered_data):
    cat_amount_df = (
        filtered_data.groupby("custom_category").agg({"Amount": "sum"}).reset_index()
    )

    return cat_amount_df

def return_name_amount_df(filtered_data):
    name_amount_df = filtered_data.groupby("Name").agg({"Amount": "sum"}).reset_index()

    return name_amount_df

def return_cat_amount_date_df(filtered_data, period="W"):
    filtered_data = filtered_data.set_index("Date")
    cat_amount_date_df = (
        filtered_data.groupby("custom_category")
        .resample(period)
        .agg({"Amount": "sum"})
        .reset_index()
    )

    return cat_amount_date_df

def calculate_smoking_adjustment(df):
    condition = (df["custom_category"] == "Groceries") & (
        df["Amount"].between(-smoke_max_value, -smoke_min_value)
    )
    adjustment_amount = df.loc[condition, "Amount"].sum()
    return adjustment_amount

def apply_smoking_adjustment(df):
    condition = (df["custom_category"] == "Groceries") & (
        df["Amount"].between(-smoke_max_value, -smoke_min_value)
    )
    df.loc[condition, "custom_category"] = "Smoking"
    return df
