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


def run():
  
streamlit run 
    st.title("Vaccination app")

    user_type = st.radio("Select your user type:", ["Hospital", "Government"])


    if user_type == "Hospital":
        st.title("Hospital Vaccination App")
    elif user_type == "Government":
        st.title("Government Vaccination App")

    if __name__ == "__main__":
        run()

