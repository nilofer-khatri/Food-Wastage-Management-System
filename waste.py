import streamlit as st
import sqlite3
import pandas as pd

# ✅ Path to your DB
DB_PATH = r"C:\Users\khatr\Downloads\sqlite\mydatabase.db"

# ✅ Connect to SQLite
conn = sqlite3.connect(DB_PATH)

st.title("🍽️ Local Food Wastage Management System")
st.markdown("Empowering communities by redistributing surplus food.")

# -------------------------------------------
# Helper Functions
# -------------------------------------------

def get_unique_values(column, table_name):
    """Fetch unique values for dropdown filters."""
    query = f"SELECT DISTINCT {column} FROM {table_name};"
    return pd.read_sql_query(query, conn)[column].dropna().tolist()

def get_provider_ids():
    """Fetch all Provider IDs."""
    query = "SELECT Provider_ID FROM providers_dataR;"
    return pd.read_sql_query(query, conn)["Provider_ID"].tolist()

def run_query(query):
    """Run any SQL query and return dataframe."""
    return pd.read_sql_query(query, conn)

# -------------------------------------------
# Sidebar Filters
# -------------------------------------------

city = st.sidebar.selectbox(
    "Filter by City", options=get_unique_values("Provider_Location", "food_listings_dataR")
)

provider = st.sidebar.selectbox(
    "Filter by Provider", options=get_unique_values("Provider_Name", "providers_dataR")
)

food_type = st.sidebar.selectbox(
    "Filter by Food Type", options=get_unique_values("Food_Type", "food_listings_dataR")
)

# -------------------------------------------
# Example Queries / Insights
# -------------------------------------------

# 1. Total Quantity of Food Available
query1 = "SELECT SUM(Quantity) AS Total_Quantity FROM food_listings_dataR;"
st.subheader("📦 Total Quantity of Food Available")
st.dataframe(run_query(query1))

# 2. Contact Providers in selected City
query_contact = f"""
SELECT Provider_Name, Contact 
FROM providers_dataR 
WHERE City = '{city}';
"""
st.subheader("📇 Contact Providers in Selected City")
st.dataframe(run_query(query_contact))

# 3. Food listings filtered by type
query_food = f"""
SELECT Food_Name, Quantity, Expiry_Date, Provider_Location, Food_Type, Meal_Type
FROM food_listings_dataR
WHERE Food_Type = '{food_type}' AND Provider_Location = '{city}';
"""
st.subheader("🥗 Food Listings (Filtered)")
st.dataframe(run_query(query_food))

# 4. Claims status distribution
query_claims = """
SELECT Claim_Status, COUNT(*) AS Total_Claims 
FROM claims_dataR 
GROUP BY Claim_Status;
"""
st.subheader("📊 Claims Distribution")
st.bar_chart(run_query(query_claims).set_index("Claim_Status"))


# -------------------------------------------
# Receivers Section
# -------------------------------------------

st.subheader("🤝 Receivers in Selected City")

query_receivers = f"""
SELECT Name, Type, Contact 
FROM receivers_dataR 
WHERE City = '{city}';
"""

st.dataframe(run_query(query_receivers))

# -------------------------------------------
# Add Food Listing Form
# -------------------------------------------

st.subheader("➕ Add New Food Listing")

with st.form("Add Food Listing"):
    food_name = st.text_input("Food Name")
    quantity = st.number_input("Quantity", min_value=1)
    expiry_date = st.date_input("Expiry Date")
    provider_id = st.selectbox("Provider ID", options=get_provider_ids())
    provider_name = st.text_input("Provider Name")
    provider_location = st.text_input("Provider Location")
    food_type = st.text_input("Food Type")
    meal_type = st.text_input("Meal Type")

    submitted = st.form_submit_button("Add Listing")

    if submitted:
        conn.execute(
            """
            INSERT INTO food_listings_dataR
            (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Name, Provider_Location, Food_Type, Meal_Type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                food_name,
                quantity,
                str(expiry_date),
                provider_id,
                provider_name,
                provider_location,
                food_type,
                meal_type,
            ),
        )
        conn.commit()
        st.success("✅ Food listing added successfully!")

