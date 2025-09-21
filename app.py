import streamlit as st

from query import (
    show_all_query,
)
from dashboard import dashboard 


def main():
    """
    Main entry point for the Streamlit Client Query Management System (CQMS) app.
    Initializes session state variables required for navigation and user management.
    Displays the sidebar navigation and routes to different pages (Dashboard, Queries, Reports, Logout)
    if the user is logged in. Handles logout logic by resetting session state and rerunning the app.
    If the user is not logged in, shows a login prompt.
    Functions called:
    - dashboard(): Displays the dashboard page.
    - show_all_query(): Displays the queries page for clients or all users.
    Session state variables used:
    - show_registration: Controls registration form visibility.
    - addClient: Controls client addition form visibility.
    - selected_query_id: Stores the currently selected query ID.
    - user_id: Stores the current user's ID.
    - logged_in: Tracks login status.
    - role: Stores the user's role (e.g., "Client").
    - username, password: Stores login credentials.
    Sidebar navigation options:
    - Dashboard
    - Querys
    - Logout
    """
    if "show_registration" not in st.session_state:
        st.session_state.show_registration = False
    if 'addClient' not in st.session_state:
        st.session_state.addClient = False
    if 'selected_query_id' not in st.session_state:
        st.session_state.selected_query_id = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # Only show page config/sidebar if logged in
    if st.session_state.get("logged_in", False):
        st.set_page_config(page_title="My Web App", layout="wide")
        st.sidebar.title("🌐 CQMS" )
        st.sidebar.write("Logged in as:", st.session_state.username)

        menu_options = ["Dashboard", "Querys", "Logout"]
        selected_option = st.sidebar.radio("Navigate", menu_options)
        
        # Page routing logic
        if selected_option == "Dashboard":
            st.subheader("📊 Client Query Management Dashboard")
            dashboard()
        elif selected_option == "Querys":
            if st.session_state.role == "Client":
                st.subheader("📋 My Querys")
                show_all_query()
            else:
                st.subheader("📋 All Querys")
                show_all_query()
        elif selected_option == "Logout":
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.password = ""
            st.session_state.role = ""
            st.session_state.addClient = False
            st.session_state.user_id = None
            st.session_state.show_registration = False
            st.success("You have been logged out.")
            st.rerun()
    else:
        # Show login page or message
        st.title("Please log in to continue.")


if __name__ == "__main__":
    main()