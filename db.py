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

def postDataToDataBase(payers, receivers):

    sa = gspread.service_account("credentials.json")
    sh = sa.open("SOL")
    worksheet = sh.get_worksheet(0)

    l = len(worksheet.col_values(1))+1

    worksheet.update_cell(l, 1, ["Lucas", "Kirill"])
    worksheet.update_cell(l, 2, ["Yulan", "Kirill"])


    
