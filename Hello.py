import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

import pandas as pd
import io
import requests
import openpyxl

# Replace <repository-url> with your GitHub repository URL
repo_url = "https://github.com/marikolk/Vaccination"

# Raw URL of the Excel file in the repository
file_path = "citizens_angola_Bengo.xlsx"
raw_url = f"{repo_url}/raw/main/{file_path}"

# Download the file from GitHub
response = requests.get(raw_url)
# Use openpyxl as the engine for reading Excel files
df_citizens = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')


# Print the first few rows to verify
st.write(df_citizens.head())

def hospital_menu():
    st.write("\nHospital Menu:")
    choice = st.selectbox("Select an option:", ["Get a Report", "Add a Patient", "Update Vaccine Status"])
  
    if choice == "Get a Report":
        st.write("Hospital: Getting a report...")
    elif choice == "Add a Patient":
        st.write("Hospital: Adding a patient...")
    elif choice == "Update Vaccine Status":
        st.write("Hospital: Updating vaccine status...")
  
  
def government_menu():
    st.write("\nGovernment Menu:")
    choice = st.selectbox("Select an option:", ["Add Citizens", "Distribute Vaccines", "Get Overall Report"])
  
    if choice == "Add Citizens":
        st.write("Government: Adding citizens...")
    elif choice == "Distribute Vaccines":
        st.write("Government: Distributing vaccines...")
    elif choice == "Get Overall Report":
        st.write("Government: Getting overall report...")

def run():

  st.title("Vaccination app")
  
  user_type = st.radio("Select your user type:", ["Hospital", "Government"])
  
  if user_type == "Hospital":
      st.title("Hospital Vaccination App")
  
      # Add a button to proceed after selecting user type
      if st.button("Continue"):
          # Call the hospital_menu function
          hospital_menu()
  
  elif user_type == "Government":
      st.title("Government Vaccination App")
  
      # Add a button to proceed after selecting user type
      if st.button("Continue"):
          # Call the government_menu function
          government_menu()
  


if __name__ == "__main__":
    run()
