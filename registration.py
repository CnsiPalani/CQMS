import streamlit as st
import hashlib
from utils import user_exists
from db import get_connection

def show_registration_page():
    """
    Displays the user registration page in the Streamlit app.
    Allows users to enter a username, password, and select a role.
    Handles registration form submission, checks for existing users,
    and provides feedback on registration success or failure.
    """
    st.title("📝 Registration")
    with st.form("registration_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Client", "Support"])
        submitted = st.form_submit_button("🟢 Register")
    if st.button("⬅️ Back to Login"):
        st.session_state.show_registration = False
        st.rerun()
    if submitted:
        try:
            if username and password and role:
                st.session_state.logged_in = False
                if user_exists(username):
                    st.error("Username already exists. Please choose a different one.")
                else:
                    pwd = hashlib.sha256(password.encode()).hexdigest()
                    if register_user(username, pwd, role):
                        st.session_state.show_registration = True
                        st.success("Registration successful!")
                    else:
                        st.error("Registration failed. Please try again.")
            else:
                st.error("All fields are required.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def register_user(username, hashed_password, role):
    """
    Registers a new user in the database.
    Args:
        username (str): The username of the new user.
        hashed_password (str): The hashed password of the new user.
        role (str): The role assigned to the new user ("Client" or "Support").

    Returns:
        bool: True if registration is successful, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, hashed_password, roles) VALUES (%s, %s, %s)",
                       (username, hashed_password, role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        if 'conn' in locals():
            conn.close()
        return False
