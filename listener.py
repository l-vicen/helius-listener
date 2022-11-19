import streamlit as st
import aiohttp
import asyncio

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
            # index = st.number_input("ID", min_value=0, max_value=100, key="index")
            address = st.text_input("Wallet Address")

            submitted = st.form_submit_button("Submit")

            if submitted:
                st.write("Result")
                data = await fetch(session, f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={API_KEY}")
                if data:
                    print(data)
                    st.write(data)
                    # st.image(data['download_url'], caption=f"Author: {data['author']}")
                else:
                    st.error("Error")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())