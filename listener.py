import streamlit as st
import moddy_credit_scorer as moddy
import aiohttp
import asyncio
import pandas as pd

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
        '(Payer | Receiver)': nativeBalanceChange,
        'Solana-Payment':paySolanaIdentifications, 
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

                    # st.write(data)

                    # Parsing data retrieved from Helius
                    dataframe = normalizeWebHookDataConnection(data)

                    # Getting the Native Balances of each Address
                    unique_addresses = moddy.getUniqueAddresses(dataframe)

                    balance_unique_addresses = []
                    for i in range(len(unique_addresses)):
                        data = await fetch(session, f"https://api.helius.xyz/v0/addresses/{unique_addresses[i]}/balances?api-key={API_KEY}")
                        balance_unique_addresses.append(data["nativeBalance"])
                    st.write("Balances")
                    st.write(balance_unique_addresses)

                    # Getting the transaction history amount
                    amount_history = moddy.getTransactionAmountHistory(dataframe, unique_addresses)

                    # Calculating Variable X for Credit Score Model
                    xs = moddy.derivingVariableX(unique_addresses, amount_history)

                    # Calculating Variable Y for Credit Score Model

                    beforeAndAfterNativeBalances = dataframe["(Payer | Receiver)"].values.tolist()
                    # st.write(beforeAndAfterNativeBalances)
                    ys = moddy.derivingVariableY(dataframe, balance_unique_addresses, unique_addresses, beforeAndAfterNativeBalances)

                    zs = moddy.derivingVariableZ(dataframe)
                    # Calculating Credit Score for every unique wallet
                    score_vector = moddy.calculateCreditScore(xs, ys, zs)

                    st.title("Credit Scores")
                    st.write(score_vector)

                else:
                    st.error("Error")

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())