from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QInputDialog, QFrame, QApplication,
                             QMenu)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPointF, QPropertyAnimation, QEasingCurve, QObject,
    QRunnable, QThreadPool, pyqtSignal,
)
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QPen, QColor

import config
from data_client import BinanceClient
import data_client


class MarketDataSignals(QObject):
    data_ready = pyqtSignal(object)
    failed = pyqtSignal(str)
    finished = pyqtSignal()


class MarketDataWorker(QRunnable):
    def __init__(self, symbols, holdings):
        super().__init__()
        self.symbols = symbols
        self.holdings = holdings
        self.signals = MarketDataSignals()

    def run(self):
        try:
            market_data = {
                symbol: BinanceClient(symbol).get_ticker_data()
                for symbol in self.symbols
            }

            current_value = 0.0
            previous_value = 0.0
            for symbol, quantity in self.holdings.items():
                if quantity <= 0:
                    continue
                ticker = market_data.get(symbol.upper())
                if ticker is None:
                    continue
                price = ticker["price"]
                previous_price = price / (1 + ticker["change"] / 100.0)
                current_value += price * quantity
                previous_value += previous_price * quantity

            change = current_value - previous_value
            percent_change = change / previous_value * 100 if previous_value else 0.0
            self.signals.data_ready.emit({
                "market_data": market_data,
                "portfolio": (current_value, percent_change, change),
            })
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            self.signals.failed.emit(str(exc))
        finally:
            self.signals.finished.emit()


class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.is_up = True
        self.setFixedHeight(25)

    def update_data(self, value, is_up=True):
        self.data.append(value)
        if len(self.data) > 15:
            self.data.pop(0)
        self.is_up = is_up
        self.update()

    def paintEvent(self, event):
        if len(self.data) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        max_val, min_val = max(self.data), min(self.data)
        range_val = max_val - min_val if max_val != min_val else 1.0

        stroke_color = QColor("#0DF042") if self.is_up else QColor("#EC0841")

        points = []
        step_x = w / (len(self.data) - 1)
        for i, val in enumerate(self.data):
            x = i * step_x
            y = h - (((val - min_val) / range_val) * (h - 4)) - 2
            points.append(QPointF(x, y))

        path = QPainterPath()
        path.moveTo(points[0])
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            cx1 = p1.x() + (p2.x() - p1.x()) / 2
            cy1, cx2, cy2 = p1.y(), p1.x() + (p2.x() - p1.x()) / 2, p2.y()
            path.cubicTo(cx1, cy1, cx2, cy2, p2.x(), p2.y())

        pen = QPen(stroke_color, 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.strokePath(path, pen)


class SymbolCard(QFrame):
    def __init__(self, symbol, remove_callback, edit_holdings_callback):
        super().__init__()
        self.symbol = symbol
        self.remove_callback = remove_callback
        self.edit_holdings_callback = edit_holdings_callback

        self.setFixedHeight(96)
        self.setObjectName("Card")
        self.lastprice = None
        
        self.setStyleSheet("""
            QFrame#Card {
                background-color: #030303;
                border: 1px solid #ffffff;
            }
        """)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_card_context_menu)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 6, 8, 6)
        self.layout.setSpacing(2)

        
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        base, quote = symbol.replace("USDT", ""), "USDT"
        self.symbol_label = QLabel(f"<span style='color: #FFFFFF; font-size: 13px; font-weight: 800;'>{base}</span><span style='color: #787B86; font-size: 11px;'> / {quote}</span>")
        self.symbol_label.setTextFormat(Qt.TextFormat.RichText)
        self.symbol_label.setStyleSheet("background: transparent; border: none;")

        

        
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedSize(22, 22)
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; color: #888888; font-weight: 700; font-size: 11px; border: none;
            }
        """)
        self.remove_btn.clicked.connect(lambda: self.remove_callback(self))
        
        self.header_layout.addWidget(self.symbol_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.remove_btn)
        
        self.layout.addLayout(self.header_layout)

        
        self.price_layout = QHBoxLayout()
        
        self.price_label = QLabel("Loading...")
        self.price_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.price_label.setStyleSheet("color: #FFFFFF; letter-spacing: -0.7px; background: transparent; border: none;")
        
        self.change_label = QLabel("--")
        self.change_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        #self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.price_layout.addWidget(self.price_label)
        self.price_layout.addStretch()
        self.price_layout.addWidget(self.change_label)
        self.price_layout.setAlignment(self.change_label, Qt.AlignmentFlag.AlignBottom)
        
        self.layout.addLayout(self.price_layout)


        self.sparkline = Sparkline()
        self.layout.addWidget(self.sparkline)

    def refresh_data(self, data):
        if not data:
            return
            
        price, change, is_up = data["price"], data["change"], data["is_up"]
        high = data.get("high",0.0)
        low = data.get("low", 0.0)
        self.setToolTip(f"<b>{self.symbol} 24h Range</b><br>High: ${high:,.2f}<br>Low: ${low:,.2f}")

        
        
        if price < 1.0:
            self.price_label.setText(f"${price:.4f}")
        else:
            self.price_label.setText(f"${price:,.2f}")
        
        sign = "+" if is_up else ""
        self.change_label.setText(f"{sign}{abs(change):.2f}%")
        self.change_label.setStyleSheet(f"color: {'#00FFA3' if is_up else '#FF3366'}; font-family: 'Consolas'; font-size: 10px; font-weight: bold; background: transparent; border: none;")

        self.sparkline.update_data(price, is_up)

        self.lastprice = price
    
    def show_card_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""QMenu {
                background-color: #121212;
                color: #E0E0E0;
                border: 1px solid #333333;
                font-family: 'Consolas';
                font-size: 11px;
                padding: 4px;
            }
            QMenu::item { padding: 4px 12px; }
        """)
        edit_action = menu.addAction("Edit Holdings")
        action = menu.exec(self.mapToGlobal(pos))
        if action == edit_action:
            self.edit_holdings_callback(self.symbol)


class DockHandle(QFrame):
    def __init__(self, hover_callback, parent=None):
        super().__init__(parent)
        self.hover_callback = hover_callback
        self.setFixedSize(7, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background-color: #00ccff; border: 1px solid #00ccff; border-radius: 30px;")

    def enterEvent(self, event):
        self.hover_callback()
        super().enterEvent(event)


class CryptoWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setFixedWidth(300)
        self.is_expanded = False
        self.position_initialized = False
        self.dock_handle_width = 5
        
        self.mainwidgetlayout = QHBoxLayout(self.central_widget)
        self.mainwidgetlayout.setContentsMargins(0, 0, 0, 0)
        self.mainwidgetlayout.setSpacing(0)

        
        self.panel = QFrame()
        self.panel.setObjectName("Panel")
        self.panel.setStyleSheet("""
            QFrame#Panel {
                background-color: #111111;
                border: 1px solid #303030;
            }
        """)
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(8, 8, 8, 8)
        panel_layout.setSpacing(8)

        self.portfolio_frame = QFrame(self.panel)
        self.portfolio_frame.setObjectName("PortfolioFrame")
        self.portfolio_frame.setStyleSheet("background: transparent; border: none;")

        portfolio_layout = QVBoxLayout(self.portfolio_frame)
        portfolio_layout.setContentsMargins(2, 2, 2, 6)
        portfolio_layout.setSpacing(4)

        self.portfolio_value = QLabel("Portfolio: $0.00")
        self.portfolio_value.setStyleSheet("font-size: 14px; font-weight: bold; color: #E8E8E8; font-family: 'Consolas';")

        self.portfolio_change = QLabel("24h Change: $0.00 (0.00%)")
        self.portfolio_change.setStyleSheet("font-size: 10px; color: #999999; background: transparent; font-family: 'Consolas';")

        portfolio_layout.addWidget(self.portfolio_value)
        portfolio_layout.addWidget(self.portfolio_change)

        panel_layout.addWidget(self.portfolio_frame)

        
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setContentsMargins(0, 4, 0, 4)
        self.cards_layout.setSpacing(6)
        
        self.cards = []
        for sym in config.SYMBOLS:
            self.add_card_ui(sym)

        self.add_btn = QPushButton("+ Add Pair")
        self.add_btn.setFixedHeight(30)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #151515;
                color: #00D890;
                border: 1px solid #303030;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 10px;
            }
        """)
        self.add_btn.clicked.connect(self.prompt_add_symbol)
        self.cards_layout.addWidget(self.add_btn)

        panel_layout.addLayout(self.cards_layout)
        self.mainwidgetlayout.addWidget(self.panel)

        self.dock_handle = DockHandle(self.expand_widget, self.central_widget)
        self.dock_handle.hide()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.refresh_worker_running = False
        self.thread_pool = QThreadPool.globalInstance()
        

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all)
        self.timer.start(config.REFRESHRATE)
        
        self.update_all()
        self.old_pos = None

        self.animation = QPropertyAnimation(self, b"pos", self)
        self.animation.setDuration(240)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self._hide_panel_when_docked)

        self.collapse_timer = QTimer(self)
        self.collapse_timer.setSingleShot(True)
        self.collapse_timer.setInterval(1000)
        self.collapse_timer.timeout.connect(self.collapse_widget)

        QTimer.singleShot(50, self.setup_initial_position)

    def show_context_menu(self, pos):
        contextmenu = QMenu(self)
        contextmenu.setStyleSheet("""
            QMenu {
                background-color: #121212;
                color: #E0E0E0;
                border: 1px solid #333333;
                font-family: 'Consolas';
                font-size: 11px;
                padding: 4px;
            }
            QMenu::item { padding: 4px 12px; }
        """)

        quit_action = contextmenu.addAction("X Quit")
        quit_action.triggered.connect(QApplication.instance().quit)

        contextmenu.exec(self.mapToGlobal(pos))


    def setup_initial_position(self):
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        y = screen.top() + (screen.height() - self.height()) // 2
        x = screen.right() + 1 - self.dock_handle_width
        self.is_expanded = False
        self.panel.hide()
        self._position_dock_handle()
        self.setGeometry(x, y, self.width(), self.height())
        self.dock_handle.show()
        self.position_initialized = True

    def _position_dock_handle(self):
        self.dock_handle.move(0, (self.central_widget.height() - self.dock_handle.height()) // 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_dock_handle()

    def enterEvent(self, event):
        if self.position_initialized:
            self.expand_widget()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.position_initialized and self.is_expanded:
            self.collapse_timer.start()
        super().leaveEvent(event)

    def expand_widget(self):
        if not self.position_initialized:
            return
        self.collapse_timer.stop()
        if self.is_expanded:
            return

        self.is_expanded = True
        self.panel.show()
        self.dock_handle.hide()
        self._animate_to_edge(expanded=True)

    def collapse_widget(self):
        if not self.is_expanded:
            return

        self.is_expanded = False
        self.dock_handle.show()
        self._position_dock_handle()
        self._animate_to_edge(expanded=False)

    def _animate_to_edge(self, expanded):
        screen = QApplication.primaryScreen().availableGeometry()
        visible_width = self.width() if expanded else self.dock_handle_width
        target_x = screen.right() + 1 - visible_width
        target_y = screen.top() + (screen.height() - self.height()) // 2

        self.animation.stop()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(target_x, target_y))
        self.animation.start()

    def _hide_panel_when_docked(self):
        if not self.is_expanded:
            self.panel.hide()


#Logic to add a new pair card
    def add_card_ui(self, symbol):
        card = SymbolCard(symbol, self.remove_card, self.open_holdings)
        self.cards.append(card)
        self.cards_layout.addWidget(card)
        QTimer.singleShot(0, self.update_position)


#Logic to remove an existing card
    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            self.cards_layout.removeWidget(card)
            card.destroyed.connect(lambda: self.update_position())
            card.deleteLater()
            self.resizeEvent(None)

    def prompt_add_symbol(self):
        
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Add +")
        dialog.setLabelText("Enter trading pair (e.g., SOLUSDT):")
        dialog.setStyleSheet("""
            QDialog { background-color: #121212; color: white; font-family: 'Consolas'; }
            QLabel { color: white; font-family: 'Consolas'; font-size: 20px; }
            QPushButton { background-color: #222; color: white; padding: 4px 10px; border: 1px solid #333; font-weight: bold; }
        """)
        
        if dialog.exec() and dialog.textValue():
            sym = dialog.textValue().strip().upper()
            if not sym.endswith("USDT"):
                sym += "USDT"
            self.add_card_ui(sym)
            self.update_all()

    def update_all(self):
        if self.refresh_worker_running:
            return

        holdings = data_client.holding_loader()
        symbols = {card.symbol for card in self.cards}
        symbols.update(
            symbol.upper()
            for symbol, quantity in holdings.items()
            if quantity > 0
        )
        worker = MarketDataWorker(symbols, holdings)
        worker.signals.data_ready.connect(self._apply_market_data)
        worker.signals.failed.connect(
            lambda message: print(f"Market data refresh failed: {message}")
        )
        worker.signals.finished.connect(self._market_data_refresh_finished)
        self.refresh_worker_running = True
        self.thread_pool.start(worker)

    def _apply_market_data(self, result):
        for card in self.cards:
            card.refresh_data(result["market_data"].get(card.symbol))
        self._apply_portfolio_data(result["portfolio"])

    def _apply_portfolio_data(self, port_data):
        self.portfolio_value.setText(f"Portfolio: ${port_data[0]:,.2f}")
        change, pct_change = port_data[2], port_data[1]
        sign = "+" if change >= 0 else "-"
        self.portfolio_change.setText(
            f"24h Change: {sign}${abs(change):,.2f} ({sign}{abs(pct_change):.2f}%)"
        )

    def _market_data_refresh_finished(self):
        self.refresh_worker_running = False

    def update_position(self):
        self.setMinimumHeight(0)
        self.adjustSize()
        if not self.position_initialized:
            return
        screen = QApplication.primaryScreen().availableGeometry()
        visible_width = self.width() if self.is_expanded else self.dock_handle_width
        target_x = screen.right() + 1 - visible_width
        target_y = screen.top() + (screen.height() - self.height()) // 2
        self.setGeometry(target_x, target_y, self.width(), self.height())

    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def open_holdings(self, symbol):
        holdings = data_client.holding_loader()
        current_amount = holdings.get(symbol, 0.0)

        amount, ok = QInputDialog.getDouble(self, "Edit Holdings", f"Enter amount of {symbol} held: ", value = current_amount, decimals=8, min=0.0)

        if ok:
            holdings[symbol] = amount
            data_client.alter_holdings(holdings)
            self.update_all()