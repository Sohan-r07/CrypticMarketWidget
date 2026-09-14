# CrypticMarketWidget

This is a live market Widget that takes data from Binance about the symbols provided and gives you continious price data and data related to the price change for the asset over the past 24 hours

This is a high-performance, frameless desktop crypto widget built with Python and PyQt6.
This is a hobby project made by me.

**Features**

**1.Futuristic Styled Ui:** Features a deep-space frosted transparent panels with hardware shadows

**2.Live Neon Price Line:** Custom rendered line chart that shows recent price movements using QPainter, completed with dynamic gradient fills and live trajectory traking.

**3.Dynamic Asset Listing:** Add any remove any trading pair listed on Binance with ease and track the markets with precision

**4.Smart Edge-Docking:** Anchors discreetly into the right edge of your screen with a glowing handle. Hover over the handle to reveal the Widget, mouse away to collapse

**5.Live Price Pulse Animation:** The borders of each asset pulse red or green corresponding to the recent change in the price!

-------------------------------------------------------------------
## Quick Start
***Quick Download the Latest version (Standalone Executablle)***

No Python setup required

1.**Download the Latest release of the Cryptic market Widget**
2.**Run the File**

The widget should appear on the right of your screen!

Right click on the widget to open the menu to close it.


## Running from Source: 

1.**Clone Repository**
```bash
git clone https://github.com/Sohan-r07/CrypticMarketWidget.git

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
  ├── config.py        # Widget settings (refresh rates, default symbols, colors)
  ├── data_client.py   # Binance REST API client for 24h ticker payload
  ├── main.py          # Application entry point & Qt event loop initializer
  └── widget_ui.py     # Core UI manager (frameless window, glassmorphic cards, QPainter sparklines)
```


**USE OF AI:**

AI was used in this project to aid in the design of the Widget UI. I usually write just bare python code and dont interact with UI design very often and had no prior experience of using PyQt6.
Hence the use of Gemini and bit of Copilot Autocomplete was used to aid in the design and speed for the Widget.
