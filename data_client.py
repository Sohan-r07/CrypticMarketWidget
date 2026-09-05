import requests


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
                "is_up": change >= 0
            }

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except (KeyError, ValueError) as e:
            #Detects any Unexpected JSON structures or errors
            print(f"Data parsing error: {e}")
            return None