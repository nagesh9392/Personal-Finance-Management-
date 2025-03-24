import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database Setup
def init_db():
    """Initialize the database and create tables if they do not exist."""
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            type TEXT,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# Call init_db to ensure tables are created before any database operations
init_db()

# Authentication Functions
def register_user(username, password):
    """Register a new user."""
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user by checking username and password."""
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Transaction Management
def add_transaction(user_id, amount, category, trans_type):
    """Add a new transaction."""
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user_id, amount, category, type, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, amount, category, trans_type, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_transactions(user_id):
    """Get all transactions for a specific user."""
    conn = sqlite3.connect("finance.db")
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df

# Streamlit UI
st.title("Personal Finance Manager")

# Sidebar Navigation
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Register":
    st.subheader("Create Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(username, password):
            st.success("Registered successfully. Please login.")
        else:
            st.error("Username already exists.")

elif menu == "Login":
    st.subheader("User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = authenticate_user(username, password)
        if user_id:
            # Store user_id in session state
            st.session_state["user_id"] = user_id
            st.success("Login successful!")
            # Redirect to dashboard after successful login
            st.experimental_rerun()  # This will refresh the page to load the dashboard

# Check if the user is logged in
if "user_id" in st.session_state:
    # Show Dashboard if logged in
    st.subheader("Dashboard")
    action = st.radio("Choose action", ["Add Transaction", "View Transactions"])

    if action == "Add Transaction":
        amount = st.number_input("Amount", min_value=0.01)
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Others"])
        trans_type = st.radio("Type", ["Income", "Expense"])
        if st.button("Add"):
            add_transaction(st.session_state["user_id"], amount, category, trans_type)
            st.success("Transaction added successfully.")

    elif action == "View Transactions":
        df = get_transactions(st.session_state["user_id"])
        st.dataframe(df)
