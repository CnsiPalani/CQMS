import streamlit as st
import pandas as pd
import re
from db import get_connection

def show_query_list_page():
    """
    Fetches and returns a list of client queries from the database.

    Depending on the user's role stored in the session state, this function retrieves either:
    - All queries (for non-client roles)
    - Only the queries associated with the current client user (for "Client" role)

    Returns:
        list: A list of tuples containing query details (query_id, emailid, mobilenumber, query_heading, query_description, status).
              Returns an empty list if an error occurs during database access.

    Raises:
        Displays an error message using Streamlit's st.error if any exception occurs.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if st.session_state.role == "Client":
            print("Fetching queries for user_id:", st.session_state.role, st.session_state.user_id)
            cursor.execute("SELECT query_id,emailid, mobilenumber, query_heading, query_description, status FROM client_query_details WHERE user_id = %s", (st.session_state.user_id,))
        else:
            cursor.execute("SELECT query_id, emailid, mobilenumber, query_heading, query_description, status FROM client_query_details")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Error fetching query list: {e}")
        return []

from st_aggrid import AgGrid, GridOptionsBuilder

def show_selectable_dataframe(df):
    search_query = st.text_input("🔍 Search all columns")
    if search_query:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        df = df[mask]

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_selection('single')
    gb.configure_column("Query ID", hide=True)
    grid_options = gb.build()
    grid_response = AgGrid(df, gridOptions=grid_options, update_mode='SELECTION_CHANGED',fit_columns_on_grid_load=True, height=355,  width='100%')
    selected = grid_response.get('selected_rows', [])
    if isinstance(selected, pd.DataFrame):
        if not selected.empty:
            query_id = selected.iloc[0]["Query ID"]
            if query_id is not None:
                st.session_state.selected_query_id = int(query_id)
                st.rerun()  # This will reload the page and show the details page
        else:
            st.info("No row selected.")
        
def show_all_query():
    if st.session_state.get("addClient", False):
        show_add_client_page()
        return
    if st.session_state.get("selected_query_id"):
        show_query_details_page(st.session_state.selected_query_id)
        return
    rows = show_query_list_page()
    df = pd.DataFrame(rows, columns=["Query ID", "Email ID", "Mobile Number", "Query Heading", "Query Description", "Status"])
    if not df.empty:
        show_selectable_dataframe(df)
    else:
        st.info("No queries found.")

def show_all_query_text():
    """
    Displays the main query management interface for the client query management system.
    The function handles the following:
    - If the 'addClient' flag is set in session state, shows the add client query page.
    - If a query is selected, shows the details page for the selected query.
    - Otherwise, displays a paginated, filterable, and searchable list of queries.
    - Allows filtering queries by status ('All', 'Open', 'Closed').
    - Supports searching queries by heading or description.
    - Provides pagination controls for navigating through the query list.
    - Renders the query list in a custom-styled table with action buttons.
    - Restricts certain actions based on the user's role (e.g., disables edit for 'Client' role).
    - Allows clients to add new queries via a button.
    - Handles and displays errors gracefully.
    Exceptions:
        Displays an error message in the Streamlit interface if any exception occurs during rendering.
    """
    try:
        if st.session_state.get("addClient", False):
            show_add_client_page()
            return
        if st.session_state.get("selected_query_id"):
            show_query_details_page(st.session_state.selected_query_id)
            return
        rows = show_query_list_page()
        if rows:
            df = pd.DataFrame(rows, columns=["Query ID", "Email ID", "Mobile Number", "Query Heading", "Query Description", "Status"])
            filter_status = st.selectbox("Filter by Status", ["All", "Open", "Closed"])
            if filter_status != "All":
                df = df[df["Status"] == filter_status]
            search_query = st.text_input("Search by Query Heading or Description")
            if search_query:
                df = df[df["Query Heading"].str.contains(search_query, case=False) | df["Query Description"].str.contains(search_query, case=False)]
            items_per_page = st.selectbox("Items per page", [5, 10, 20, 50], index=1)
            total_pages = len(df) // items_per_page + (len(df) % items_per_page > 0)
            if total_pages == 0:
                st.info("No queries found for the selected filters/search.")
                return
            page_number = st.number_input("Page number", min_value=1, max_value=total_pages, value=1)
            start_idx = (page_number - 1) * items_per_page
            end_idx = start_idx + items_per_page
            paginated_df = df.iloc[start_idx:end_idx]
            st.write(f"Showing page {page_number} of {total_pages}")

            st.markdown("""
            <style>
            .table-container {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            .table-header, .table-row {
                display: flex;
                border-bottom: 1px solid #ddd;
                padding: 5px 0;
            }
            .table-header div, .table-row div {
                flex: 1;
                padding: 0 10px;
                font-size: 14px;
            }
            .table-header {
                font-weight: bold;
                background-color: #f0f0f0;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="table-container">
                <div class="table-header">
                    <div>Action</div>
                    <div>Email ID</div>
                    <div>Mobile Number</div>
                    <div>Query Heading</div>
                    <div>Query Description</div>
                    <div>Status</div>
                </div>
            """, unsafe_allow_html=True)

            for _, row in paginated_df.iterrows():
                cols = st.columns([1,2,2,2,3,1])
                with cols[0]:
                    if st.button("✏️", key=f"view_{row['Query ID']}",disabled=True if st.session_state.role == "Client" else False):
                        st.session_state.selected_query_id = row["Query ID"]
                        st.write(f"Selected Query ID: {row['Query ID']}")  # Debug print
                        st.rerun()
                cols[1].write(row["Email ID"])
                cols[2].write(row["Mobile Number"])
                cols[3].write(row["Query Heading"])
                cols[4].write(row["Query Description"])
                cols[5].write(row["Status"])

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.info("No queries found.")

        if st.session_state.role == "Client":
            if st.button("➕ Add Client Query"):
                st.session_state.addClient = True
                st.rerun()
    except Exception as e:
        st.error(f"Error displaying queries: {e}")

def show_query_details_page(query_id):
    """
    Displays and manages the update page for a specific client query in a Streamlit app.

    Args:
        query_id (int or str): The unique identifier of the client query to display and update.

    Functionality:
        - Fetches query details from the database using the provided query_id.
        - Displays the query details in a form with fields for Email ID, Mobile Number, Query Heading, Query Description, and Status.
        - All fields except Status are displayed as disabled (read-only).
        - Allows the user to update the Status of the query.
        - Validates the form input before updating the database.
        - Updates the query details in the database upon form submission.
        - Displays success or error messages based on the operation outcome.
        - Provides a button to return to the list of all queries.

    Exceptions:
        - Handles and displays errors if fetching or updating query details fails.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT query_id, emailid, mobilenumber, query_heading, query_description, status, screenshot FROM client_query_details WHERE query_id = %s", (query_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            st.title("📋Update Client Query Page")
            with st.form("update_client_form"):
                emailid = st.text_input("Email ID", value=result[1], disabled=True)
                mobile_number = st.text_input("Mobile Number", value=result[2], disabled=True)
                query_heading = st.text_input("Query Heading", value=result[3], disabled=True)
                query_description = st.text_area("Query Description", value=result[4], disabled=True)
                if result[6]:
                    st.image(result[6], caption="Existing Screenshot", use_container_width=True, clamp=True, channels="RGB")
                else:
                    st.image("https://via.placeholder.com/400x300.png?text=No+Screenshot", caption="No Screenshot Available", use_container_width=True) 
                    
                status = st.selectbox("Status", ["Open", "Closed"], index=0 if result[5] == "Open" else 1)
                submitted = st.form_submit_button("Update Client Query")
                if submitted:
                    if not emailid or not mobile_number or not query_heading or not query_description:
                        st.error("All fields are required.")
                    elif not is_valid_email(emailid):
                        st.error("Please enter a valid Email ID.")
                    else:
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE client_query_details
                                SET emailid = %s, mobilenumber = %s, query_heading = %s, query_description = %s, status = %s
                                WHERE query_id = %s
                            """, (emailid, mobile_number, query_heading, query_description, status, query_id))
                            conn.commit()
                            conn.close()
                            st.success("Client query updated successfully!")
                            st.session_state.selected_query_id = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating query: {e}")
            if st.button("🔙 Back to All Query"):
                st.session_state.selected_query_id = None
                st.rerun()
        else:
            st.error("Query not found.")
    except Exception as e:
        st.error(f"Error fetching query details: {e}")

def is_valid_email(email):
    """
    Validates whether the provided email address is in a correct format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address is valid, False otherwise.

    Raises:
        Displays an error message using Streamlit if an exception occurs during validation.
    """
    try:
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None
    except Exception as e:
        st.error(f"Error validating email: {e}")
        return False

def show_add_client_page():
    """
    Displays the "Add Query" page in the Streamlit app, allowing users to submit a new client query.
    The page includes a form for entering the following fields:
        - Email ID
        - Mobile Number
        - Query Heading
        - Query Description
    Features:
        - Validates that all fields are filled.
        - Validates the email format.
        - Inserts the query into the 'client_query_details' database table with status 'Open' and the current user's ID.
        - Displays success or error messages based on the outcome.
        - Provides a button to return to the "My Queries" page.
    Exceptions:
        - Handles and displays errors related to form submission, database operations, and page rendering.
    """
    try:
        st.title("📝 Add Query")
        with st.form("add_client_form"):
            emailid = st.text_input("Email ID")
            mobile_number = st.text_input("Mobile Number")
            query_heading = st.text_input("Query Heading")
            query_description = st.text_area("Query Description")
            screenshot = st.file_uploader("Upload Screenshot", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("✅Submit Query")

        if st.button("⬅️ Back to My Queries"):
            st.session_state.addClient = False
            st.rerun()

        if submitted:
            if not emailid or not mobile_number or not query_heading or not query_description:
                st.error("All fields are required.")
            elif not is_valid_email(emailid):
                st.error("Please enter a valid Email ID.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    screenshot_bytes = screenshot.read() if screenshot else None
                    cursor.execute("""
                        INSERT INTO client_query_details (emailid, mobilenumber, query_heading, query_description, status, user_id, screenshot)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (emailid, mobile_number, query_heading, query_description, 'Open', st.session_state.user_id, screenshot_bytes))
                    conn.commit()
                    conn.close()
                    st.success("Client query added successfully!")
                    st.session_state.addClient = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding client query: {e}")
    except Exception as e:
        st.error(f"Error displaying add client page: {e}")

def show_all_data():
    """
    Fetches all client query details from the database.

    Returns:
        list: A list of tuples containing query details. If the user role is "Client", only queries associated with the user's ID are returned; otherwise, all queries are returned.

    Raises:
        Displays an error message using Streamlit if an exception occurs during data retrieval.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if st.session_state.role == "Client":
            cursor.execute("SELECT query_id, emailid, mobilenumber, query_heading, query_description, query_created_time, status, query_closed_time FROM client_query_details WHERE user_id = %s order by query_created_time desc", (st.session_state.user_id,))
        else:
            cursor.execute("SELECT query_id, emailid, mobilenumber, query_heading, query_description, query_created_time, status, query_closed_time FROM client_query_details order by query_created_time desc")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Error fetching all data: {e}")
        return []
