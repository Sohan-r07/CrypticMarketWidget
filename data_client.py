import requests
import json
import os
Holdings = "holdings.json"


class BinanceClient:
    def __init__(self, symbol):

        self.symbol = symbol
        self.base_url = "https://api.binance.com/api/v3/ticker/24hr"

    def get_ticker_data(self):
        """We get the latest price of the asset for the symbol
        
        This returns a dictionary with the latest price and other relevant information for the specified symbol.
        """   

        try:
            url = f"{self.base_url}?symbol={self.symbol}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()  # Raise an exception for HTTP errors


            data = response.json()

            price = float(data["lastPrice"])
            change = float(data["priceChangePercent"])

            #Returning the Data fetched from the Binance API

            return {
                "price": price,
                "change": change,
                "high": float(data["highPrice"]),
                "low": float(data["lowPrice"]),
                "is_up": change >= 0

            }

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except (KeyError, ValueError) as e:
            #Detects any Unexpected JSON structures or errors
            print(f"Data parsing error: {e}")
            return None

def holding_loader():
    if os.path.exists(Holdings):
        try:
            with open(Holdings, "r") as holdings_data:
                return json.load(holdings_data)
        except:
            return {}
    return {}

def alter_holdings(holdings_dict):
    try:
        with open(Holdings,"w") as holdings_data:
            json.dump(holdings_dict, holdings_data, indent=4)
    except Exception as e:
        print(f"Error writing changes to the holding file: {e}")

def calculate_portfolio():
    holdings = holding_loader()
    total_previous_value = 0.0
    total_current_value = 0.0

    #Loop through the symbols and get their data
    for symbol, quantity in holdings.items():
        cap_symbol = symbol.upper()
        datasource = BinanceClient(cap_symbol)
        if quantity > 0.0:

            pricedata = datasource.get_ticker_data()
            if pricedata is None:
                print(f"Failed to fetch data for {cap_symbol}. Skipping this symbol.")
                continue
            curr_price = pricedata["price"]
            changepct = pricedata["change"]

            #calculate previous price based on change and current price
            prev_price = curr_price / (1+(changepct/100.0))

            #Update current portfolio value
            total_current_value += curr_price * quantity
            total_previous_value += prev_price * quantity

    change = total_current_value - total_previous_value
    pct_change = (change/total_previous_value * 100) if total_previous_value !=0 else 0.0


    return [total_current_value, pct_change, change]