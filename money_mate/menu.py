import streamlit as st
from streamlit_option_menu import option_menu

# 1. as sidebar menu
with st. sidebar:
    selected = option_menu(
    menu_title="Main Menu", #required
    options=['PCN Dashboard', 'Surgery Dashboard', 'Feedback Classification', 'Improvement Suggestions', 'Semitment Analysis'],
    icons=["house", "book", "envelope", "book", "envelope"],
    menu_icon="cast", #optional
    default_index=0, #optional #required
    )

if selected == "Home":
    st.title(f"You have selected {selected}")
if selected == "Projects":
    st.title(f"You have selected {selected}")
