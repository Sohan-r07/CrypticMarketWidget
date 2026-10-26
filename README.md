# CrypticMarketWidget

This is a simple desktop widget that shows coin price changes over the past 24 hours 
and also the immediate changes in price over the past minute.
The price data is recieved from the Binance API.
This widget is built in Python and PyQt6.


**Features**

**1.Futuristic Styled UI:** Features a deep-space frosted transparent panels with hardware shadows

**2.Live Price Line:** A Live price line that shows the changes in price over a short period of time.

**3.Customizable Assets List:** Add any remove any trading pair listed on Binance with ease and track the markets with precision


**5.Live Price Pulse Animation:** The borders of each asset pulse red or green corresponding to the recent change in the price!

-------------------------------------------------------------------

## Quick Start
***Quick Download the Latest version (Standalone Executablle)***

This methon requires no Python setup.

1.**Download the Latest release of the Cryptic market Widget**
2.**Run the File**

The widget should appear on the right of your screen!

Right click on the widget to open the menu to close it.


## Running from Source: 

1.**Clone Repository**
```bash
git clone [https://github.com/Sohan-r07/CrypticMarketWidget.git](https://github.com/Sohan-r07/CrypticMarketWidget.git)

cd CrypticMarketWidget
```
2.**Install dependencies**

```bash
#Create a Venv
python -m venv .venv

#Windows
.venv\Scripts\activate.bat

#Linux and macOS
source myenv/bin/activate

#Install all required libraries
pip install -r requirements.txt
```

3.**Launch the widget!**

```bash
python main.py
```

**Addition Tips:**

Add the CrypticmarketWidget.exe to your startup files so that the Widget starts on your system start up!

**Project structure:**

```bash
CrypticMarketWidget
  ├── config.py        # Widget settings(contains refreshrate, colours, etc)
  ├── data_client.py   # Binance REST API client for 24h ticker payload
  ├── main.py          # Application entry point & Qt event loop initializer
  └── widget_ui.py     # Core UI manager (frameless window, glassmorphic cards, QPainter sparklines)
```


**USE OF AI:**

AI was used in this project to aid in the design of the Widget UI. I usually write just bare python code and dont interact with UI design very often and had no prior experience of using PyQt6.
Hence the use of Gemini and bit of Copilot Autocomplete was used to aid in the design and speed for the Widget.

**IMPORTANT:**

The ReadMe is not written with AI, I have written it myself with the help of youtube tutorials about how to make professional ReadMe's 
and all the things about styling that i have learn't while observing other Github Repositories.