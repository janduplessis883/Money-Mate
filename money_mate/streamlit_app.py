import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_shadcn_ui as ui

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
            ui.badges(badge_list=[("Incorrect Passcode, please try again.", "destructive")], class_name="flex gap-2", key="error1")

# Check if the user is authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
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

    budget = conn.read(
        worksheet="Budget",
        ttl="10m",
    )

    if tabs == "Account Summary":
        pass

    elif tabs == "Budget":
        pass

    elif tabs == "Account History":
        pass

    elif tabs == "View | Update - Budget":
        with st.expander(label="Budget - DataFrame"):
            st.dataframe(budget)

        with st.expander(label="Budget - Google Sheet"):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?gid=1571834654#gid=1571834654"
            st.components.v1.html(f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>', height=600)


    elif tabs == "View | Update - Bank Statement":
        with st.expander(label="Account Statement - DataFrame"):
            st.dataframe(data)

        with st.expander(label="Account Statement - Google Sheet"):
            # Embed Google Sheet in an expander
            google_sheet_url = "https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?usp=sharing"
            st.components.v1.html(f'<iframe src="{google_sheet_url}" width="100%" height="600"></iframe>', height=600)

# https://docs.google.com/spreadsheets/d/1bpW10hRPxTDwQ1UjEBsKLKwZ9tf9RTFl91GQhVv1luI/edit?usp=sharing
