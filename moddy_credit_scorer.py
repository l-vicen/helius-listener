import streamlit as st
import numpy as np
import pandas as pd
import time

DIV_COEFF = 133.225

def getUniqueAddresses(dataframe):
    # Get unique addresses
    list_unique_payers = list(dict.fromkeys(dataframe.Payer.values.tolist()))
    # st.write("Unique Addresses")
    # st.write(list_unique_payers)
    return list_unique_payers

def getTransactionAmountHistory(dataframe, unique_addresses):
    # Getting Balance History for Variance Calculation
    amount_history = []
    for i in range(len(unique_addresses)):
        amount_history_user_specific = []
        for index, row in dataframe.iterrows():
            if (unique_addresses[i] == row["Payer"]):
                amount_history_user_specific.append(row["Amount"])
            else:
                continue
            
        amount_history.append(amount_history_user_specific)

    # st.write("History Amount")
    # st.write(amount_history)
    return amount_history

def derivingVariableX(unique_addresses, amount_history):
    # Calculating Variance
    variance = []
    for i in range(len(unique_addresses)): 
        variance.append(np.var(amount_history[i]))
    # st.write("Variance of each Wallet")
    # st.write(variance)

    varX_preTunning = [0 if variableX >= 200 else (variableX + 0.02) for variableX in variance]
    # st.write("VarPreTunning")
    # st.write(varX_preTunning)

    variable_x = [(1 / varX) if varX != 0.0 else 0.0 for varX in varX_preTunning]
    # st.write("varX_tunned")
    # st.write(variable_x)
    return variable_x

def derivingVariableY(dataframe, balances, unique_addresses, beforeAndAfterNativeBalances):

    # Total Number of Transaction per Address
    transactions_per_payer = dataframe['Payer'].value_counts()
    # st.write("Transaction per Payer")
    # st.write(transactions_per_payer)

    addresses = dataframe["Payer"].values.tolist()
    tuple_changes = dataframe["(Payer | Receiver)"].values.tolist()

    payouts = []
    for k in range(len(balances)):
        pay = 0
        for i,j in zip(addresses, tuple_changes):
            if unique_addresses[k] == i:
                pay += j[0]
                # payouts.append(j[0])
        payouts.append(pay)

    # st.write("Payouts")
    # st.write(payouts)

    start_balance = np.subtract(balances, payouts)
    # st.write("Start Balances")
    # st.write(start_balance)

    adj_vector = [x / y for x, y in zip(payouts, transactions_per_payer)]
    # st.write("Adjusted by number transactions")
    # st.write(adj_vector)

    adj_vector_div_half = [x / 2 for x in adj_vector]
    # st.write("Scaling")
    # st.write(adj_vector_div_half)

    trig_behavior = [((np.arctan(x) / (0.65)) + 0.05) for x in adj_vector_div_half]
    # st.write("Trigonometric Adjustment")
    # st.write(trig_behavior)

    variable_y = [0 if element < 0 else element for element in trig_behavior]
    # st.write("Transformer")
    # st.write(variable_y)
    return variable_y

def derivingVariableZ(dataframe):
    timeStamp = dataframe.groupby('Payer')['Date'].apply(lambda x: list(np.unique(x))).reset_index(name="Timestamps")
    timeStamp["Count Timestamps"] = timeStamp["Timestamps"].str.len()
    timeStamp["Min Date"] = timeStamp["Timestamps"].apply(lambda x: min(x))
    timeStamp["Max Date"] = timeStamp["Timestamps"].apply(lambda x: max(x))

    # st.write('Unique Timestamps')
    # st.write(timeStamp)

    # l_timestamp_count = timeStamp["Count Timestamps"].values.tolist()
    l_min_date_count = timeStamp["Min Date"].values.tolist()
    l_max_date_count = timeStamp["Max Date"].values.tolist()

    time_right_now = time.time()
    # st.write("Time Right Now")
    # st.write(time_right_now)

    # condition_one = [0 if l_timestamp_count[i] < 1 else i for i in l_timestamp_count]

    vector_variable_time = [ (time_right_now - first_activity) for first_activity in l_min_date_count]
    variable_z_pre = [1 if (time_right_now - latests_activity) > 90 else (np.square(vector_variable_time) / DIV_COEFF) for latests_activity in l_max_date_count]
    variable_z = [2.2 if z > 2.2 else z for z in variable_z_pre]
    return variable_z


def calculateCreditScore(variable_x, variable_y, variable_z, wallets):
    credit_scores = np.multiply.reduce((variable_x, variable_y, variable_z))
    d = {'Wallets': wallets, 'Credit Scores': credit_scores}
    return pd.DataFrame(d)  


