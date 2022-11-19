import streamlit as st
import aiohttp
import asyncio
import pandas as pd

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
                    # data.get(0)["timestamp"]
                    # st.table(data) # For table representation
                    # st.write(data) # For dict representation
                    normalizeWebHookDataConnection(data)

                else:
                    st.error("Error")

def normalizeWebHookDataConnection(data):

    timestamps = [data[i]["timestamp"] for i in range(len(data))]
    fromUsersAccounts = [data[i]["nativeTransfers"][0]["fromUserAccount"] for i in range(len(data))]
    toUsersAccounts = [data[i]["nativeTransfers"][0]["toUserAccount"] for i in range(len(data))]
    amounts = [data[i]["nativeTransfers"][0]["amount"] for i in range(len(data))]

    paySolanaIdentifications = []
    for i in range(len(data)):
        isSolPayTransaction = False
        for j in range(len(data[i]["accountData"])):
            if data[i]["accountData"][j]["account"] == "F6mQcTMvnPcp9JEKbjvgidrfUD14FojoZtJk4GEQ9bAa":
                paySolanaIdentifications.append(data[i]["accountData"][j]["account"])
                isSolPayTransaction = True
            else:
                continue

        if isSolPayTransaction == False:
            paySolanaIdentifications.append("NOT_SOLANA_PAY_TRANSACTION")

    productsBundle = []
    for i in range(len(data)):
        productPurchase = False
        for j in range(len(data[i]["accountData"])):
            if data[i]["accountData"][j]["account"] == "3V7ZHQoouyJ8NuTfzdcQExF3QvXRSwxabdrxv1x5RFpW": # BANANA IDENTIFIER
                productsBundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
            elif data[i]["accountData"][j]["account"] == "ADsyD7QSXpTPBDzJFq4geAFnEPD1NrCKExqseeMDYBbh": # APPLE IDENTIFIER
                productsBundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
            elif data[i]["accountData"][j]["account"] == "DCVTCuAs3VuzxoUQAV5hHaXbnuB7xdXsnXjv1xUoWTa3": # BEER IDENTIFIER
                productsBundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
            elif data[i]["accountData"][j]["account"] == "5Gwy6Ga6461DDHfb6kLMKP7GpCLCMWWBggwjrKfeenNo": # PRETZEL IDENTIFIER
                productsBundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
            elif data[i]["accountData"][j]["account"] == "YPDGKRbLAihKdkNGyz4R3CP8HYohBByfQSWnSiUEJHU": # CHEESE IDENTIFIER
                productsBundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
            else:
                continue

        if productPurchase == False:
            productsBundle.append("NO_PRODUCT_PURCHASE")
    
    # st.write(timestamps)
    # st.write(fromUsersAccounts)
    # st.write(toUsersAccounts)
    # st.write(amounts)
    # st.write(paySolanaIdentifications)
    # st.write(productsBundle)

    d = {'Payer':fromUsersAccounts,
        'Receiver':toUsersAccounts,
        'Date':timestamps,
        'Amount':amounts,
        'Solana-Payment':paySolanaIdentifications, 
        'Products':productsBundle}

    df_parsed = pd.DataFrame.from_dict(d)
    st.table(df_parsed)

def normalizeTimestamp():
    pass

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())