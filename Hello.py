# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

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
