# Dependencies
import streamlit as st
import pandas as pd
from gsheetsdb import connect
import gspread

DB_TARGET_URL = "https://docs.google.com/spreadsheets/d/1TscPz0hQe8PbnS3gfssrYM21K_n4N1RR4kxAnWHjodc/edit?usp=sharing"

def getDataFromDataBase():
    conn = connect()
    rows = conn.execute(f'SELECT * FROM "{DB_TARGET_URL}"')
    df_gsheet = pd.DataFrame(rows)
    st.table(df_gsheet)

def postDataToDataBase():
    pass


    
