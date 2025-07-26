import streamlit as st
from utils.db_handler import save_user_db

def login_ui(role, USER_DB):
    username = st.text_input(f"{role} Username", key=f"{role}_user")
    password = st.text_input("Password", type="password", key=f"{role}_pass")
    if st.button("Login", key=f"{role}_btn"):
        if username in USER_DB[role] and USER_DB[role][username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = role
        else:
            st.error("Invalid credentials")

def register_ui(role, USER_DB, USER_INFO, WATCHLIST_DB):
    username = st.text_input("Username", key=f"{role}_username")
    email = st.text_input("Email", key=f"{role}_email")
    mobile = st.text_input("Mobile Number", key=f"{role}_mobile")
    password = st.text_input("Password", type="password", key=f"{role}_password")

    if st.button("Register", key=f"{role}_reg_btn"):
        if username in USER_DB[role]:
            st.warning("User already exists")
        else:
            USER_DB[role][username] = password
            USER_INFO[role][username] = {"email": email, "mobile": mobile}
            if role == "remote_users":
                WATCHLIST_DB[username] = []
            save_user_db({
                "user_db.json": USER_DB,
                "user_info.json": USER_INFO,
                "watchlist_db.json": WATCHLIST_DB,
            })
            st.success("Registered successfully!")
