import streamlit as st
import aiohttp
import asyncio
import pandas as pd

import moody_credit_scorer as moody
import db as db

st.set_page_config(
    page_title="heliusListener", 
    page_icon="🤖"
 )

API_KEY = "52f6ef1c-a919-490c-8d25-ccebe7a5947b"

def normalizeWebHookDataConnection(data):

    # Parsing Helius Queried Data
    timestamps = [data[i]["timestamp"] for i in range(len(data))]
    # st.success("Successfuly queried Timestamps")

    fromUsersAccounts = [data[i]["nativeTransfers"][0]["fromUserAccount"] for i in range(len(data))]
    # st.success("Successfuly queried fromUsersAccounts")

    toUsersAccounts = [data[i]["nativeTransfers"][0]["toUserAccount"] for i in range(len(data))]
    # st.success("Successfuly queried toUsersAccounts")
    
    amounts = [data[i]["nativeTransfers"][0]["amount"] for i in range(len(data))]
    # st.success("Successfuly queried amounts")

    # Getting Native Balance Moves (+ or -)
    nativeBalanceChange = []
    for i in range(len(data)):
        balancePayerReciever = (data[i]["accountData"][0]["nativeBalanceChange"], data[i]["accountData"][1]["nativeBalanceChange"])
        nativeBalanceChange.append(balancePayerReciever)
    # st.success("Successfuly queried nativeBalanceChange")
    
    # Identifying Solana Payment Transactions from normal transactions
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

    # st.success("Successfuly queried paySolanaIdentifications")

    # Building Product Bundle
    productsBundle = []
    for i in range(len(data)):
        productPurchase = False
        bundle = []
        for j in range(len(data[i]["accountData"])):
            if data[i]["accountData"][j]["account"] == "3V7ZHQoouyJ8NuTfzdcQExF3QvXRSwxabdrxv1x5RFpW": # BANANA IDENTIFIER
                bundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
                continue
            if data[i]["accountData"][j]["account"] == "ADsyD7QSXpTPBDzJFq4geAFnEPD1NrCKExqseeMDYBbh": # APPLE IDENTIFIER
                bundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
                continue
            if data[i]["accountData"][j]["account"] == "DCVTCuAs3VuzxoUQAV5hHaXbnuB7xdXsnXjv1xUoWTa3": # BEER IDENTIFIER
                bundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
                continue
            if data[i]["accountData"][j]["account"] == "5Gwy6Ga6461DDHfb6kLMKP7GpCLCMWWBggwjrKfeenNo": # PRETZEL IDENTIFIER
                bundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
                continue
            if data[i]["accountData"][j]["account"] == "YPDGKRbLAihKdkNGyz4R3CP8HYohBByfQSWnSiUEJHU": # CHEESE IDENTIFIER
                bundle.append(data[i]["accountData"][j]["account"])
                productPurchase = True
                continue

        if productPurchase == False:
            productsBundle.append(["NO_PRODUCT_PURCHASE"])
        else:
            productsBundle.append(bundle)

    # st.write(productsBundle)
    # st.success("Successfuly queried productsBundle")
    
    d = {'Payer':fromUsersAccounts,
        'Receiver':toUsersAccounts,
        'Date':timestamps,
        'Amount':amounts,
        'Native_Balance_Change': nativeBalanceChange,
        'Solana_Payment':paySolanaIdentifications, 
        'Products':productsBundle}

    df_parsed = pd.DataFrame.from_dict(d)
    st.table(df_parsed)
    return df_parsed

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            result = await response.json()
            return result
    except Exception:
        return {}

async def main():

    st.markdown("# Helius Listener")
    st.info("This tool was created to facilitate the prototyping of our Credit Scorer project. As our solution is to some extent serverless. We built this tool to communicate with the WebHooks provided by Helius.\n The Helius Listener Project does not have a robust UI iteration yet, however if the user uncomment some st.write() statements in the source he will see the logic behind this tool. \n The tool is responsible for: \n- (1) Communicating with Helius;  \n- (2) Parsing Helius data; \n- (3) Apply the Credit Score Algorithm (mooddy_credit_scorer.py) is crucial nonetheless; \n- (4) Feed Data to DB @GoogleAPI&Sheet;")
    
    async with aiohttp.ClientSession() as session:

        with st.form("my_form"):
            address = st.text_input("Wallet Address")
            list_query_option = ['nft-events','nfts','transactions', 'raw-transactions','names','balances']
            target = st.selectbox("Query Options", list_query_option)

            submitted = st.form_submit_button("Submit")

            if submitted:
                st.markdown("## On-chain Results")
                data = await fetch(session, f"https://api.helius.xyz/v0/addresses/{address}/{target}?api-key={API_KEY}")
                if data:

                    # st.write(data)
                    # # Parsing data retrieved from Helius
                    dataframe = normalizeWebHookDataConnection(data)

                    # Getting the Native Balances of each Address
                    unique_addresses = moody.getUniqueAddresses(dataframe)
                    # st.write(unique_addresses)

                    balance_unique_addresses = []
                    for i in range(len(unique_addresses)):
                        data = await fetch(session, f"https://api.helius.xyz/v0/addresses/{unique_addresses[i]}/balances?api-key={API_KEY}")
                        balance_unique_addresses.append(data["nativeBalance"])
                    
                    # st.write("Balances")
                    # st.write(balance_unique_addresses)

                    # Getting the transaction history amount
                    amount_history = moody.getTransactionAmountHistory(dataframe, unique_addresses)

                    # Calculating Variable X for Credit Score Model
                    xs = moody.derivingVariableX(unique_addresses, amount_history)

                    # Calculating Variable Y for Credit Score Model

                    beforeAndAfterNativeBalances = dataframe["Native_Balance_Change"].values.tolist()
                    # st.write(beforeAndAfterNativeBalances)
                    ys = moody.derivingVariableY(dataframe, balance_unique_addresses, unique_addresses, beforeAndAfterNativeBalances)

                    zs = moody.derivingVariableZ(dataframe)
                    # Calculating Credit Score for every unique wallet
                    cs_df = moody.calculateCreditScore(xs, ys, zs, unique_addresses)
                    db.postDataCS(cs_df) # Creating the DB & Feeding it

                    st.write('---')
                    st.markdown("## Wallet & Credit Scores ")
                    st.info("Due to low volume of transaction & wallets the credit score algorithm sets all CF to 0. \n It is still worthwhile to have a look on the incentives of the algorithm, either by reading the doc or talking to us!")
                    st.write(cs_df)

                else:
                    st.error("Error")
                    st.warning("No activity of this query type was found for this wallet. Change the wallet or the query request!")

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())