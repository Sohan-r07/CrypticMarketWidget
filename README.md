# CrypticMarketWidget

This is a live market Widget that takes data from Binance about the symbols provided and gives you continious price data and data related to the price change for the asset over the past 24 hours

This is a high-performance, frameless desktop crypto widget built with Python and PyQt6.
This is a hobby project made by me.

**Features**

**1.Futuristic Styled Ui:** Features a deep-space frosted transparent panels with hardware shadows

**2.Live Neon Price Line:** Custom rendered line chart that shows recent price movements using QPainter, completed with dynamic gradient fills and live trajectory traking.

**3.Dynamic Asset Listing:** Add any remove any trading pair listed on Binance with ease and track the markets with precision

**4.Smart Edge-Docking:** Anchors discreetly into the right edge of your screen with a glowing handle. Hover over the handle to reveal the Widget, mouse away to collapse

-------------------------------------------------------------------
## Quick Start
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