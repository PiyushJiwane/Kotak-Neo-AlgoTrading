from neo_api_client import NeoAPI

import dotenv
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
dotenv_path = ".env"

# Read stock information from CSV
df = pd.read_csv('./stock_info.csv')

# Initialize dictionaries from the DataFrame
orderPlaced = df.set_index('instrument_token')['orderPlaced'].to_dict()
targetPrices = df.set_index('instrument_token')['target_price'].to_dict()
quantities = df.set_index('instrument_token')['quantity'].to_dict()
pTrdSymbol = df.set_index('instrument_token')['stockName'].to_dict()

consumer_key=os.getenv("CONSUMER_KEY")
consumer_secret=os.getenv("CONSUMER_SECRET")
mobile_number=os.getenv("MOBILE_NUMBER")
password=os.getenv("PASSWORD")
# otp=input("Enter an OTP : ")
otp=os.getenv("OTP")

def orderPlace(data):
    global orderPlaced  # Use the global flag
    symbol = data.get("tSymbol")
    if not orderPlaced[symbol]:
        sPrice = data.get("price")
        sQuantity = data.get("quantity")
        sSymbol =  pTrdSymbol[data.get("tSymbol")]
        placed = client.place_order(
            exchange_segment='nse_cm', product='MIS', price='0',
            order_type='MKT', quantity=sQuantity, validity='DAY', trading_symbol=sSymbol,
            transaction_type='B', amo="NO", disclosed_quantity="0", market_protection="0",
            pf="N", trigger_price='0', tag=None
        )
        print(placed)
        orderPlaced[symbol] = True  # Set the flag to True after placing the order for this stock

def on_message(message):
    global orderPlaced  # Use the global flag
    for stock in message:
        symbol = int(stock.get('tk'))
        ltp = stock.get('ltp')
        if symbol in orderPlaced and not orderPlaced[symbol]:
            target_price = targetPrices.get(symbol, None)
            if target_price is not None and ltp is not None and float(ltp) >= target_price:
                orderPlace({"price": str(target_price), "quantity": str(quantities[symbol]), "tSymbol":symbol, "orderPlaced": orderPlaced[symbol]})

# def on_message(message):
#     if(message[0].get('ltp')!=None):
#         # print(float(message[0].get('ltp')))
#         # print(type(float(message[0].get('ltp'))))
#         if(float(message[0].get('ltp'))>=817):
#             orderPlace({"price":"817","quantity":"1","tSymbol":"SBIN-EQ","orderPlaced":False})
#     # if(message[0].get('tbq')!=None and message[0].get('tsq')!=None and message[0].get('v')!=None):
#     #     print(f'{message[0].get("nc")} - {(int(message[0].get("v"))-int(message[0].get("tbq"))+int(message[0].get("tsq")))} - {message[0].get("tbq")} - {message[0].get("tsq")}')
    
def on_error(error_message):
    print(error_message)

client = NeoAPI(consumer_key=consumer_key,
                consumer_secret=consumer_secret, 
                environment='PROD', on_message=on_message, on_error=on_error, on_close=None, on_open=None)

token=client.login(mobilenumber=mobile_number, password=password)

dotenv.set_key(dotenv_path, "TOKEN", token.get("data").get("token"))

client.session_2fa(OTP=otp)

inst_tokens = df.apply(lambda row: {"instrument_token": str(row['instrument_token']), "exchange_segment": "nse_cm"}, axis=1).tolist()

client.subscribe(instrument_tokens=inst_tokens, isIndex=False, isDepth=False)[0]