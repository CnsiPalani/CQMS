import hashlib
import streamlit as st
from db import get_connection
from registration import show_registration_page  # Add this import if the function is defined in registration.py

def show_login_page():
    """
    Displays the login page using Streamlit, allowing users to log in or register as a new user.

    The function renders a login form with fields for username, password, and role selection ("Client" or "Support").
    Upon form submission, it attempts to authenticate the user using the `login_user` function.
    If authentication is successful, updates session state with user details and reruns the app.
    If authentication fails, displays an error message and resets relevant session state variables.
    Also provides a button for new user registration, which sets a session state flag to show the registration page.

    Session State Variables Modified:
        - show_registration: Flag to display registration page.
        - logged_in: Boolean indicating login status.
        - username: Stores the entered username.
        - password: Stores the entered password.
        - role: Stores the selected role.
        - user_id: Stores the authenticated user's ID (if login is successful).

    Exceptions:
        - Catches and displays any exceptions that occur during login.

    Returns:
        None
    """
    st.title("🔒 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("🔑 Login")
    if st.button("📝 New User Registration"):
        st.session_state.show_registration = True
        st.rerun()
    if submitted:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.password = password
        
        try:
            result = login_user(username, password)
            if result:
                st.success("Login successful!")
                st.session_state.user_id = result.get('id')
                st.session_state.role = result.get('role')
                print(f"Logged in as user_id: {st.session_state.user_id}, role: {st.session_state.role}")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
                st.session_state.user_id = None
                st.session_state.logged_in = False
                return
        except Exception as e:
            st.error(f"An error occurred during login: {e}")
            st.session_state.user_id = None
            st.session_state.logged_in = False
            return

def login_user(username, password):
    """
    Authenticates a user based on username and password.

    Args:
        username (str): The username of the user attempting to log in.
        password (str): The plaintext password provided by the user.

    Returns:
        dict or None: A dictionary containing user information ('id', 'username') if authentication is successful; None otherwise.

    Raises:
        Exception: Prints error message if any exception occurs during authentication.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        pwd = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND hashed_password=%s",
            (username, pwd)
        )
        result = cursor.fetchall()
        if result:
            user = {'id': result[0][0], 'username': result[0][1], 'role': result[0][3]}
        else:
            user = None
        conn.close()
        return user
    except Exception as e:
        print(f"Error in login_user: {e}")
        return None

def logout():
    """
    Logs out the current user by resetting relevant session state variables.

    This function sets the user's authentication and session-related variables to their default values,
    effectively logging out the user from the application. If an error occurs during the process,
    an error message is displayed.

    Raises:
        Displays an error message in the Streamlit app if an exception occurs during logout.
    """
    try:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.session_state.role = ""
        st.session_state.addClient = False
        st.session_state.user_id = None
        st.session_state.show_registration = False
    except Exception as e:
        st.error(f"An error occurred during logout: {e}")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_registration" not in st.session_state:
    st.session_state.show_registration = False

if st.session_state.logged_in:
    from app import main
    main()
elif st.session_state.show_registration:
    show_registration_page()
else:
    show_login_page()
