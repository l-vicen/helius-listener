# Dependencies
import streamlit as st

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

# Post / Writing Request to construct own DB at Google Sheets  
def postDataCS(dataframe):
    """Example of post-alike request which fills own DB @GoogleAPI&Sheets
    with a pairs:

      0:  <Wallet | Credit Score>
      . . . . 

    The sad reality is that due to low transaction history of our tables the credit scoring algo
    scores all on-chain transanction with credit of 0. The worst credit.... 

    Nonetheless, the mathematics of the model seem accurate (revision is possible by uncommenting st.writes(...))
    and out calculators and desmos graphical calculator double-checked our local results. Detailed doc on how
    the algorithm works can be found @ the respective file.
    """
    sa = gspread.service_account("credentials.json")
    sh = sa.open("hackaTUM")
    worksheetCS = sh.get_worksheet(1)
    worksheetCS.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    


    
