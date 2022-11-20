# Dependencies
import streamlit as st
import pandas as pd

from google.oauth2 import service_account
from gsheetsdb import connect
import gspread

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

def getDataSOL():
    sheet_url = st.secrets["private_gsheets_url"]
    rows = run_query(f'SELECT * FROM "{sheet_url}"')
    df_gsheet = pd.DataFrame(rows)
    st.table(df_gsheet)
    return df_gsheet

def getDataSheetCS():
    pass

def postDataSOL(dataframe):
    pass
  
def postDataCS(dataframe):
    sa = gspread.service_account("credentials.json")
    sh = sa.open("hackaTUM")
    worksheetCS = sh.get_worksheet(1)
    worksheetCS.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

def postDataMA(dataframe):
    pass

    


    
