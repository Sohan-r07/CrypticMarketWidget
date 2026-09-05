import sys
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QInputDialog, QFrame, QApplication,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QPen, QColor, QLinearGradient

import config
from data_client import BinanceClient

class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.is_up = True
        self.setFixedHeight(32)

    def update_data(self, value, is_up=True):
        self.data.append(value)
        if len(self.data) > 12:
            self.data.pop(0)
        self.is_up = is_up
        self.update()

    def paintEvent(self, event):
        if len(self.data) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pad_x, pad_y = 5, 5
        w = self.width() - (pad_x * 2)
        h = self.height() - (pad_y * 2)

        max_val, min_val = max(self.data), min(self.data)
        range_val = max_val - min_val if max_val != min_val else 1.0

        # High-visibility neon colors
        stroke_color = QColor("#00FFA3") if self.is_up else QColor("#FF3366")
        fill_color = QColor(0, 255, 163, 40) if self.is_up else QColor(255, 51, 102, 40)

        points = []
        step_x = w / (len(self.data) - 1)
        for i, val in enumerate(self.data):
            x = pad_x + (i * step_x)
            y = pad_y + h - (((val - min_val) / range_val) * h)
            points.append(QPointF(x, y))

        path = QPainterPath()
        path.moveTo(points[0])

        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            cx1 = p1.x() + (p2.x() - p1.x()) / 2
            cy1, cx2, cy2 = p1.y(), p1.x() + (p2.x() - p1.x()) / 2, p2.y()
            path.cubicTo(cx1, cy1, cx2, cy2, p2.x(), p2.y())

        # Gradient fill beneath the curve
        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1].x(), self.height())
        fill_path.lineTo(points[0].x(), self.height())
        fill_path.closeSubpath()
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, fill_color)
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillPath(fill_path, gradient)

        # Main stroke
        pen = QPen(stroke_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.strokePath(path, pen)

        # Glowing dot at the current price head
        last_point = points[-1]
        painter.setPen(Qt.PenStyle.NoPen)
        
        glow_color = QColor(stroke_color)
        glow_color.setAlpha(60)
        painter.setBrush(glow_color)
        painter.drawEllipse(last_point, 5.0, 5.0)

        painter.setBrush(stroke_color)
        painter.drawEllipse(last_point, 2.0, 2.0)


class SymbolCard(QFrame):
    def __init__(self, symbol, remove_callback):
        super().__init__()
        self.symbol = symbol
        self.remove_callback = remove_callback
        self.client = BinanceClient(symbol)
        
        self.setFixedSize(260, 115)
        self.setObjectName("Card")
        
        # Dark Glassmorphism with "Light Catcher" directional borders
        self.setStyleSheet("""
            QFrame#Card {
                background-color: rgba(16, 19, 26, 220);
                border-radius: 12px;
                border-top: 1px solid rgba(255, 255, 255, 18);
                border-left: 1px solid rgba(255, 255, 255, 18);
                border-bottom: 1px solid rgba(255, 255, 255, 4);
                border-right: 1px solid rgba(255, 255, 255, 4);
            }
            QFrame#Card:hover {
                background-color: rgba(22, 26, 35, 240);
                border-top: 1px solid rgba(0, 255, 163, 60);
                border-left: 1px solid rgba(0, 255, 163, 60);
            }
        """)

        # Hardware shadow for physical depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(4)

        # --- Top Header Row ---
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Live Sync Dot
        self.live_dot = QFrame()
        self.live_dot.setFixedSize(6, 6)
        self.live_dot.setStyleSheet("background-color: #5C6170; border-radius: 3px;") 

        # Symbol Label
        base, quote = symbol.replace("USDT", ""), "USDT"
        self.symbol_label = QLabel(f"<span style='color: #FFFFFF; font-size: 13px; font-weight: 800;'>{base}</span><span style='color: #787B86; font-size: 11px;'> / {quote}</span>")
        self.symbol_label.setTextFormat(Qt.TextFormat.RichText)
        self.symbol_label.setStyleSheet("background: transparent; border: none;")

        # Formally integrated Remove Button (no absolute positioning)
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedSize(22, 22)
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; color: #5C6170; border-radius: 11px; font-weight: 900; font-size: 10px; border: none; 
            }
            QPushButton:hover { 
                background: rgba(255, 51, 102, 0.2); color: #FF3366; 
            }
        """)
        self.remove_btn.clicked.connect(lambda: self.remove_callback(self))
        
        self.header_layout.addWidget(self.live_dot)
        self.header_layout.addSpacing(4)
        self.header_layout.addWidget(self.symbol_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.remove_btn)
        
        self.layout.addLayout(self.header_layout)

        # --- Price and Change Row ---
        self.price_layout = QHBoxLayout()
        
        self.price_label = QLabel("Syncing...")
        self.price_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.price_label.setStyleSheet("color: #FFFFFF; letter-spacing: -0.5px; background: transparent; border: none;")
        
        self.change_label = QLabel("--")
        self.change_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.price_layout.addWidget(self.price_label)
        self.price_layout.addStretch()
        self.price_layout.addWidget(self.change_label)
        self.price_layout.setAlignment(self.change_label, Qt.AlignmentFlag.AlignBottom)
        
        self.layout.addLayout(self.price_layout)

        # --- Sparkline Row ---
        self.sparkline = Sparkline()
        self.layout.addWidget(self.sparkline)

    def refresh_data(self):
        data = self.client.get_ticker_data()
        if not data:
            return
            
        price, change, is_up = data["price"], data["change"], data["is_up"]
        
        # Human touch: adjust decimal places for micro-caps vs majors
        if price < 1.0:
            self.price_label.setText(f"${price:.4f}")
        else:
            self.price_label.setText(f"${price:,.2f}")
        
        sign = "+" if is_up else ""
        self.change_label.setText(f"{sign}{change:.2f}%")

        if is_up:
            self.change_label.setStyleSheet("color: #00FFA3; background: rgba(0, 255, 163, 15); border-radius: 4px; padding: 2px 6px; border: none;")
            self.live_dot.setStyleSheet("background-color: #00FFA3; border-radius: 3px;")
        else:
            self.change_label.setStyleSheet("color: #FF3366; background: rgba(255, 51, 102, 15); border-radius: 4px; padding: 2px 6px; border: none;")
            self.live_dot.setStyleSheet("background-color: #FF3366; border-radius: 3px;")

        self.sparkline.update_data(price, is_up)


class CryptoWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_h_layout = QHBoxLayout(self.central_widget)
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setSpacing(0)

        # --- Sleek Hover Handle (Cyberpunk style) ---
        self.handle_container = QWidget()
        self.handle_container.setFixedWidth(16)
        handle_layout = QVBoxLayout(self.handle_container)
        handle_layout.setContentsMargins(0, 0, 0, 0)
        handle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.handle = QFrame()
        self.handle.setFixedSize(4, 60)
        self.handle.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 255, 163, 80);
                border-radius: 2px;
            }
            QFrame:hover {
                background-color: rgba(0, 255, 163, 255);
            }
        """)
        
        handle_shadow = QGraphicsDropShadowEffect(self)
        handle_shadow.setBlurRadius(12)
        handle_shadow.setColor(QColor(0, 255, 163, 150))
        handle_shadow.setOffset(0, 0)
        self.handle.setGraphicsEffect(handle_shadow)
        
        handle_layout.addWidget(self.handle)
        self.main_h_layout.addWidget(self.handle_container)

        # --- Main Cards Container ---
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(5, 15, 15, 15)
        self.cards_layout.setSpacing(12)
        
        self.cards = []
        for sym in config.SYMBOLS:
            self.add_card_ui(sym)

        self.add_btn = QPushButton("+ Initialize Data Stream")
        self.add_btn.setFixedSize(260, 38)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 255, 163, 5);
                color: #00FFA3;
                border-radius: 8px;
                border: 1px dashed rgba(0, 255, 163, 40);
                font-family: 'Consolas'; font-weight: bold; font-size: 11px; letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 163, 20);
                border: 1px solid rgba(0, 255, 163, 80);
                color: #FFFFFF;
            }
        """)
        self.add_btn.clicked.connect(self.prompt_add_symbol)
        self.cards_layout.addWidget(self.add_btn)

        self.main_h_layout.addWidget(self.cards_container)

        # --- Slide Animation Setup ---
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.animation.setDuration(450)
        self.is_expanded = False
        self.dialog_open = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all)
        self.timer.start(config.REFRESHRATE)
        
        self.update_all()
        self.old_pos = None

        QTimer.singleShot(50, self.setup_initial_position)

    def setup_initial_position(self):
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.width() - 16  # Snaps to right edge, leaving only the 16px handle visible
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

    def add_card_ui(self, symbol):
        card = SymbolCard(symbol, self.remove_card)
        self.cards.append(card)
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            self.cards_layout.removeWidget(card)
            card.hide() # Instantly hide for responsive feel
            card.deleteLater()
            QTimer.singleShot(10, self.update_position)

    def prompt_add_symbol(self):
        self.dialog_open = True
        
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Initialize Asset")
        dialog.setLabelText("Enter trading pair (e.g., SOLUSDT):")
        dialog.setStyleSheet("""
            QDialog { background-color: #0F1219; color: white; }
            QLabel { color: white; font-family: 'Segoe UI'; font-weight: bold; }
            QLineEdit { background-color: #161A23; color: #00FFA3; font-family: 'Consolas'; border: 1px solid #333; padding: 4px; border-radius: 4px;}
            QPushButton { background-color: #1E232F; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #2D3446; border: 1px solid #00FFA3; }
        """)
        
        ok = dialog.exec()
        text = dialog.textValue()
        self.dialog_open = False
        
        if ok and text:
            self.add_card_ui(text.strip().upper())
            self.update_position()
            self.cards[-1].refresh_data()
            
        if not self.underMouse():
            self.animate_drawer(False)

    def update_all(self):
        for card in self.cards:
            card.refresh_data()

    def update_position(self):
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        target_x = screen.width() - self.width() if self.is_expanded else screen.width() - 16
        self.setGeometry(target_x, self.y(), self.width(), self.height())

    def enterEvent(self, event):
        if not self.is_expanded:
            self.animate_drawer(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.dialog_open: 
            return
        if self.is_expanded:
            self.animate_drawer(False)
        super().leaveEvent(event)
        
    def animate_drawer(self, expand):
        self.is_expanded = expand
        self.animation.stop()
        
        screen = QApplication.primaryScreen().availableGeometry()
        start_rect = self.geometry()
        target_x = screen.width() - self.width() if expand else screen.width() - 16
        
        end_rect = QRect(target_x, start_rect.y(), self.width(), self.height())
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            new_y = self.pos().y() + delta.y()
            
            # Constrain to screen vertical boundaries
            screen = QApplication.primaryScreen().availableGeometry()
            new_y = max(screen.top(), min(new_y, screen.bottom() - self.height()))
            
            self.move(self.pos().x(), new_y) 
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None