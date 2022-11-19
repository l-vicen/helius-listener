import streamlit as st
import aiohttp
import asyncio
import pandas as pd
import csv

API_KEY = "52f6ef1c-a919-490c-8d25-ccebe7a5947b"

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            result = await response.json()
            return result
    except Exception:
        return {}


async def main():
    st.set_page_config(page_title="heliusListener", page_icon="🤖")
    st.title("Helius Listener")
    async with aiohttp.ClientSession() as session:

        with st.form("my_form"):
            address = st.text_input("Wallet Address")
            list_query_option = ['nft-events','nfts','transactions', 'raw-transactions','names','balances']
            target = st.selectbox("Query Options", list_query_option)

            submitted = st.form_submit_button("Submit")

            if submitted:
                st.write("Result")
                data = await fetch(session, f"https://api.helius.xyz/v0/addresses/{address}/{target}?api-key={API_KEY}")
                if data:
                    st.table(data) # For table representation
                    st.write(data) # For dict representation
                else:
                    st.error("Error")

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())