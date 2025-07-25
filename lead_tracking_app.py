import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json

# --- Sidebar Config ---
st.set_page_config(page_title="FOOD Talent Lead Tracker", layout="wide")
st.title("🧠 GPT-Powered FOOD Talent Lead Tracker")

# --- Use Streamlit Secrets (no manual upload) ---
sheet_name = "FOOD-Talent-Library"  # hardcoded, or make it editable if needed

import json
openai_api_key = st.secrets["OPENAI_API_KEY"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

if sheet_name and openai_api_key:
    # Authenticate with Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gspread_client = gspread.authorize(creds)

    try:
        sheet = gspread_client.open(sheet_name).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        st.subheader("📋 Current Leads")
        st.dataframe(df)

        # GPT Query Section
        st.subheader("💬 Ask GPT About Your Leads")
        user_query = st.text_area(
            "Ask a question about your leads:",
            placeholder="e.g. Who should I follow up with in London?"
        )

        if st.button("Run Query") and user_query:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)

            prompt = f"""
You are an assistant helping manage creative talent leads. Here's the current table of leads:

{df.to_markdown(index=False)}

Based on this, answer the following question:

{user_query}
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            st.markdown("### 🤖 GPT Response")
            st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error accessing sheet: {e}")

else:
    st.warning("⬅️ Please upload credentials and enter your keys to proceed.")
