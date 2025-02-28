import streamlit as st
import numpy as np
import pandas as pd
import pdfplumber
from datetime import datetime, time

# Function to get free rooms
def get_free_rooms(df, query_date, query_time):
    # query_date = pd.to_datetime(query_date).date()
    # query_time = pd.to_datetime(query_time, format="%H:%M").time()
    all_rooms = set(df["Room No."].unique())
    occupied_rooms = set(df[(df["Date"].dt.date == query_date) &
                            (df["Start Time"] <= query_time) &
                            (df["End Time"] > query_time)]["Room No."].unique())
    return sorted(list(all_rooms - occupied_rooms))

# Streamlit UI
st.title("Room Availability Checker")

# Load Data

# Path to the uploaded PDF
pdf_path = "./MIDSEM.pdf"

# Extract text from the PDF
data = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_table()
        if tables:
            data.extend(tables)

# Convert to DataFrame
df = pd.DataFrame(data)

# Rename columns and remove irrelevant rows
df = df.iloc[3:]  # Remove header rows
df.columns = ["Course Code", "Course Name", "Date & Time", "Room No.", "Student Range", "No. of Students"]

# Reset index
df = df.reset_index(drop=True)

# Remove rows where 'Room No.' is None (these are likely header rows)
df = df[df["Room No."].notna()]

# Clean whitespace and newlines
df = df.map(lambda x: x.replace("\n", " ") if isinstance(x, str) else x)

# Extract Date, Start Time, End Time separately
df[["Date", "Time Range"]] = df["Date & Time"].str.split(" - ", expand=True)
df[["Start Time", "End Time"]] = df["Time Range"].str.split(" to ", expand=True)

# Drop the original Date & Time column
df = df.drop(columns=["Date & Time", "Time Range"])

# Convert time to 24-hour format for better querying
df["Start Time"] = pd.to_datetime(df["Start Time"], format="%I:%M %p").dt.time
df["End Time"] = pd.to_datetime(df["End Time"], format="%I:%M %p").dt.time

df["Date"] = pd.to_datetime(df["Date"], format="%d %B %y")

# Filling empty columns with NaNs
df.replace(r'^\s+', np.nan, regex=True)
df = df.ffill()

# Query 1: Find free rooms
st.header("Check Free Rooms")
st.write("The app works only during Midsem week from 3rd March to 8th March. Enter times from 9 AM to 6 PM only.")
query_date = st.date_input("Select Date", min_value=df["Date"].min(), max_value=df["Date"].max())
query_time = st.time_input("Select Time")
if st.button("Find Free Rooms"):
    free_rooms = get_free_rooms(df, query_date, query_time)
    st.write(f"### Free Rooms at {query_time} on {query_date}:")
    st.write("\n\n".join(free_rooms) if free_rooms else "No free rooms available.")