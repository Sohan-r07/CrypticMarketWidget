import sys
from PyQt6.QtWidgets import QApplication
from widgetui import CryptoWidget  

#Now for the Main loop
def main():
    app = QApplication(sys.argv)

    widget = CryptoWidget()
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
