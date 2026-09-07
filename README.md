# CrypticMarketWidget

This is a live market Widget that takes data from Binance about the symbols provided and gives you continious price data and data related to the price change for the asset over the past 24 hours

This is a high-performance, frameless desktop crypto widget built with Python and PyQt6.
This is a hobby project made by me. I have been involved with **Crypto-Currencies** and **Blockchains** from a very long time.
The technology and its usecases are truly amazing and very exciting to me.
This is a simple project I wanted to build so that I can monitor crypto
 pairs while doing other tasks.

 <img width="352" height="552" alt="image_2026-09-05_154046923" src="https://github.com/user-attachments/assets/82862e9b-bee7-4a5a-81dc-af7714cbe4d6" />

**Features**

**1. Futuristic Styled Ui:** Features a deep-space frosted transparent panels with hardware shadows

**2. Live Neon Price Line:** Custom rendered line chart that shows recent price movements using QPainter, completed with dynamic gradient fills and live trajectory tracking.

**3. Dynamic Asset Listing:** Add any remove any trading pair listed on Binance with ease and track the markets with precision

**4. Smart Edge-Docking:** Anchors discreetly into the right edge of your screen with a glowing handle. Hover over the handle to reveal the Widget, mouse away to collapse

-------------------------------------------------------------------
## Quick Start
1.**Clone Repository**
```python
git clone https://github.com/Sohan-r07/CrypticMarketWidget.git

cd CrypticMarketWidget
```

2.**Install Dependencies**
```text
#Create a Venv
python -m venv .venv

#Windows
.venv\Scripts\activate.bat

#Linux and macOS
source myenv/bin/activate

#Install all required libraries
pip install -r requirements.txt

```

3.**Launch the Widget**
```bash
python main.py
```

You should see the glowing handle for the Widget on the side of your screen.

**Tips:**

To make the widget start on startup:

**Windows:**

1. Press Win + R, type shell:startup, and press Enter to open your Windows Startup folder.

2. Right-click inside the folder, select New -> Shortcut.

3. In the location field, paste the path pointing to your virtual environment's pythonw.exe (which hides the terminal window) and your main.py:
```bash
"C:\path\to\CrypticMarketWidget\.venv\Scripts\pythonw.exe" "C:\path\to\CrypticMarketWidget\main.py"
#(Make sure to replace C:\path\to\CrypticMarketWidget with your actual absolute project path).
```
4. Click Next, name it CrypticMarketWidget, and click Finish.

**Linux or Ubuntu:**
1. Create a new autostart desktop entry file:
```bash
nano ~/.config/autostart/cryptic-widget.desktop
```
2. Paste the following configuration and change "/path/to/CrypticMarketWidget" to your actual path
```ini
[Desktop Entry]
Type=Application
Name=Cryptic Market Widget
Exec=/path/to/CrypticMarketWidget/.venv/bin/python /path/to/CrypticMarketWidget/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

3. Save and exit (Ctrl + O, then Enter, then Ctrl + X).



**Project Structure**
```bash
CrypticMarketWidget
  |-----------config.py        --> Manages all the settings for the Widget like the Refreshrate, Default Symbols and Font colours
  |-----------data_client.py   --> Used to fetch all the required data from Binance
  |-----------main.py          --> The main file for the Widget that manages everything
  |-----------widgetui.py      --> The main Widget UI manager that manages all the styling and design of the Widget
```


**Credits:**
The use of Google Gemini was made to help with the designing of the Widget UI itself.
Github Copilot autocomplete was used in the development to aid speed.
