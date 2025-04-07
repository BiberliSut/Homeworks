import sys
import os
import random
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, QSize, QPoint, QRect
from PySide6.QtGui import QColor, QPainter, QFont, QIcon, QPixmap, QLinearGradient, QPainterPath, QRadialGradient, QPen, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect, QSizePolicy,
    QStackedWidget, QGridLayout
)

# Color constants - Darker background and gray tones
DARK_BG = QColor(8, 10, 14)  # Darker background
TEXT_COLOR = QColor(200, 200, 200)
ACTIVE_COLOR = QColor(0, 255, 128)  # Green for active status

# Light beam and particle animation for background
class BackgroundEffects(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Skin tone particles (light beige to soft brown)
        self.particles = [{
            'x': random.randint(0, parent.width()),
            'y': random.randint(0, parent.height()),
            'size': random.randint(2, 8),
            'speed_x': random.uniform(-1.0, 1.0),
            'speed_y': random.uniform(-1.0, 1.0),
            'opacity': random.uniform(0.1, 0.9),
            'color': random.choice([
                QColor(255, 222, 173, int(255 * random.uniform(0.1, 0.3))),  # Light skin tone
                QColor(238, 203, 173, int(255 * random.uniform(0.1, 0.3))),  # Medium light skin tone
                QColor(222, 184, 135, int(255 * random.uniform(0.1, 0.3)))   # Medium skin tone
            ])
        } for _ in range(200)]

        # Light beam properties from top-left corner
        self.beam_angle = 45  # Diagonal beam
        self.beam_width = int(parent.width() * 0.4)
        self.beam_opacity = 0.2
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_effects)
        self.timer.start(30)

    def update_effects(self):
        # Update particle positions
        for p in self.particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            
            # Bounce off edges
            if p['x'] < 0 or p['x'] > self.parent().width():
                p['speed_x'] *= -1
            if p['y'] < 0 or p['y'] > self.parent().height():
                p['speed_y'] *= -1
                
        # Animate beam opacity for subtle pulsing effect
        self.beam_opacity = 0.15 + 0.05 * abs(math.sin(datetime.now().timestamp()))
                
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw light beam from top-left corner
        painter.save()        
        beam_gradient = QLinearGradient(0, 0, self.parent().width(), self.parent().height())
        beam_gradient.setColorAt(0, QColor(255, 222, 173, int(255 * self.beam_opacity * 1.5)))
        beam_gradient.setColorAt(0.3, QColor(238, 203, 173, int(255 * self.beam_opacity * 0.8)))
        beam_gradient.setColorAt(1, QColor(222, 184, 135, 0))
        
        # Create beam path
        beam_path = QPainterPath()
        beam_path.moveTo(0, 0)  # Top-left corner
        beam_path.lineTo(self.beam_width, 0)
        beam_path.lineTo(self.parent().width(), self.parent().height() - 100)
        beam_path.lineTo(self.parent().width() - self.beam_width, self.parent().height())
        beam_path.lineTo(0, self.beam_width)
        beam_path.closeSubpath()
        
        painter.fillPath(beam_path, beam_gradient)
        painter.restore()
        
        # Draw particles
        for p in self.particles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(p['color'])
            painter.drawEllipse(p['x'], p['y'], p['size'], p['size'])


class SignalStrengthIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 20)
        self._signal_level = 0

        self.animation = QPropertyAnimation(self, b"signal_level")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(3)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def get_signal_level(self):
        return self._signal_level

    def set_signal_level(self, level):
        self._signal_level = level
        self.update()

    signal_level = Property(float, get_signal_level, set_signal_level)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bar_width = 5
        spacing = 2
        height = self.height()

        for i in range(4):
            bar_height = (i + 1) * (height / 4)
            x = i * (bar_width + spacing)
            y = height - bar_height

            if i <= self._signal_level:
                painter.setBrush(QColor(TEXT_COLOR))
            else:
                painter.setBrush(QColor(100, 100, 100, 100))

            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 1, 1)


class SensorPanel(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        # Darker panel background
        self.setStyleSheet("background-color: rgba(0, 0, 0, 220); border-radius: 12px;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.signal_icon = SignalStrengthIcon()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: white; font-size: 14px;")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("NO SIGNAL")
        self.status_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.signal_icon, 0, Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.status_label)

        self.active = False

    def set_active(self, active):
        self.active = active
        if active:
            self.signal_icon.animation.setDirection(QPropertyAnimation.Forward)
            self.signal_icon.animation.start()
            self.status_label.setText("ACTIVE")
            self.status_label.setStyleSheet(f"color: {ACTIVE_COLOR.name()}; font-size: 16px; font-weight: bold;")
        else:
            self.signal_icon.animation.setDirection(QPropertyAnimation.Backward)
            self.signal_icon.animation.start()
            self.status_label.setText("NO SIGNAL")
            self.status_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")


class MenuButton(QPushButton):
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(20, 20, 25, 180);
                color: white;
                border-radius: 10px;
                padding: 10px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 45, 200);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 65, 220);
            }
        """)
        self.setFixedHeight(45)
        
        if icon_name:
            # Try SVG icon path first, then PNG
            icon_path_svg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", f"{icon_name}.svg")
            icon_path_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", f"{icon_name}.png")
            
            if os.path.exists(icon_path_svg):
                self.setIcon(QIcon(icon_path_svg))
                self.setIconSize(QSize(16, 16))
            elif os.path.exists(icon_path_png):
                self.setIcon(QIcon(icon_path_png))
                self.setIconSize(QSize(16, 16))


class SideMenu(QWidget):
    def __init__(self, menu_type="settings", parent=None):
        super().__init__(parent)
        self.setFixedWidth(0)  # Initially closed
        self.setStyleSheet("background-color: rgba(15, 15, 20, 240); border-top-right-radius: 20px; border-bottom-right-radius: 20px;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Menu title based on type
        self.menu_type = menu_type
        self.title = QLabel(self.get_title_for_type(menu_type))
        self.title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title)
        
        # Menu buttons based on type
        self.buttons = []
        for text, icon in self.get_items_for_type(menu_type):
            btn = MenuButton(text, icon)
            self.layout.addWidget(btn)
            self.buttons.append(btn)
        
        self.layout.addStretch()
        
        # Add exit button at bottom
        self.exit_btn = MenuButton("Çıkış", "exit")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(180, 30, 30, 180);
                color: white;
                border-radius: 10px;
                padding: 10px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(220, 40, 40, 200);
            }
        """)
        self.layout.addWidget(self.exit_btn)
        
        # Animation properties
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.is_open = False
    
    def get_title_for_type(self, menu_type):
        titles = {
            "settings": "AYARLAR",
            "usb": "USB BAĞLANTI",
            "equalizer": "VERİ İZLEME",
            "volume": "SES KONTROLÜ",
            "pen": "KAYIT",
            "camera": "KAMERA AYARLARI",
            "wifi": "BAĞLANTI YÖNETİMİ",
            "location": "KONUM BİLGİSİ",
            "next": "DİĞER AYARLAR"
        }
        return titles.get(menu_type, "AYARLAR")
    
    def get_items_for_type(self, menu_type):
        # Define menu items based on type
        menus = {
            "settings": [
                ("Sistem Ayarları", "settings"),
                ("Görünüm", "display"),
                ("Performans", "cpu"),
                ("Gizlilik", "privacy"),
                ("Güncelleme", "update")
            ],
            "camera": [
                ("Kamera Seçimi", "camera"),
                ("Çözünürlük", "resolution"),
                ("Gece Görüşü", "night"),
                ("Kayıt Ayarları", "record"),
                ("Sensör Ayarları", "sensor")
            ],
            "wifi": [
                ("Wifi Ayarları", "wifi"),
                ("Bluetooth", "bluetooth"),
                ("Ağ Durumu", "network"),
                ("VPN Ayarları", "vpn"),
                ("Cihaz Eşleştirme", "pairing")
            ],
            "equalizer": [
                ("Grafik Görünümü", "chart"),
                ("Veri Kaynakları", "database"),
                ("Alarmlar", "alarm"),
                ("Raporlama", "report"),
                ("Veri Arşivi", "archive")
            ],
            "volume": [
                ("Ses Düzeyi", "volume"),
                ("Ses Kaynakları", "mic"),
                ("Bildirim Sesleri", "notification"),
                ("Ekolayzer", "equalizer"),
                ("Çıkış Cihazı", "speaker")
            ],
            "pen": [
                ("Not Defteri", "notes"),
                ("Çizim Modu", "pen"),
                ("Belge İşlemleri", "document"),
                ("Paylaşım", "share"),
                ("Şablonlar", "template")
            ],
            "usb": [
                ("USB Cihazları", "usb"),
                ("Veri Transferi", "transfer"),
                ("Güvenlik", "security"),
                ("Sürücüler", "driver"),
                ("Harici Depolama", "storage")
            ],
            "location": [
                ("Konum Servisleri", "location"),
                ("Harita Görünümü", "map"),
                ("Rota Planlama", "route"),
                ("Konum Geçmişi", "history"),
                ("Konum Bildirimleri", "notification")
            ],
            "next": [
                ("Diğer Ayarlar", "more"),
                ("Lisans Bilgisi", "license"),
                ("Hakkında", "about"),
                ("Geri Bildirim", "feedback"),
                ("Gelişmiş Ayarlar", "advanced")
            ]
        }
        return menus.get(menu_type, [])
    
    def toggle(self):
        self.is_open = not self.is_open
        
        if self.is_open:
            self.animation.setStartValue(0)
            self.animation.setEndValue(250)
        else:
            self.animation.setStartValue(250)
            self.animation.setEndValue(0)
        
        self.animation.start()


class BottomToolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)  # Reduced height for more compact toolbar
        self.setStyleSheet("background-color: white; border-radius: 20px;")
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Inner layout for buttons
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(15, 5, 15, 5)
        self.layout.setSpacing(10)  # Reduced spacing
        
        # Container for buttons
        container = QWidget()
        container.setLayout(self.layout)
        container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        
        # Center align container
        main_layout.addStretch(1)
        main_layout.addWidget(container)
        main_layout.addStretch(1)

        self.buttons = []
        icon_names = ["settings", "usb", "equalizer", "volume", "pen", "camera", "exit", "wifi", "location", "next"]
        
        # Icon file paths
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        
        # Here you can add a comment about SVG icon paths
        # Comment: Here SVG icons' file paths should be defined. If SVG files are not found, PNG will be used instead.
        
        for name in icon_names:
            btn = QPushButton()
            btn.setFixedSize(28, 28)  # Smaller button size
            
            # Try SVG first, then PNG
            icon_file_svg = os.path.join(icon_path, f"{name}.svg")
            icon_file_png = os.path.join(icon_path, f"{name}.png")
            
            if os.path.exists(icon_file_svg):
                icon = QIcon(icon_file_svg)
                btn.setIcon(icon)
                btn.setIconSize(QSize(18, 18))
            elif os.path.exists(icon_file_png):
                icon = QIcon(icon_file_png)
                btn.setIcon(icon)
                btn.setIconSize(QSize(18, 18))
            else:
                btn.setText("")
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 10);
                    border-radius: 14px;
                }
                QPushButton:pressed {
                    background-color: rgba(0, 0, 0, 20);
                }
            """)
            btn.setProperty("icon_name", name)
            self.layout.addWidget(btn)
            self.buttons.append(btn)


class DynamicIsland(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 50)
        self.setStyleSheet("background-color: white; border-radius: 25px;")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 5, 15, 5)
        self.layout.setSpacing(10)
        
        # Time widget
        self.time = QLabel()
        self.date = QLabel()
        self.time.setStyleSheet("color: black; font-size: 16px; font-weight: bold;")
        self.date.setStyleSheet("color: black; font-size: 12px;")
        
        time_container = QWidget()
        time_layout = QVBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(0)
        time_layout.addWidget(self.time)
        time_layout.addWidget(self.date)
        
        # Weather icon and temperature
        self.weather_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        weather_icon_file = os.path.join(icon_path, "weather.svg")
        weather_png_file = os.path.join(icon_path, "weather.png")
        
        if os.path.exists(weather_icon_file):
            pixmap = QPixmap(weather_icon_file)
            self.weather_icon.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif os.path.exists(weather_png_file):
            pixmap = QPixmap(weather_png_file)
            self.weather_icon.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.weather_icon.setText("☀️")
            self.weather_icon.setStyleSheet("font-size: 18px;")
        
        self.temp = QLabel("25°C")
        self.temp.setStyleSheet("color: black; font-size: 16px; font-weight: bold;")
        self.day = QLabel("Tuesday")
        self.day.setStyleSheet("color: black; font-size: 12px;")
        
        weather_container = QWidget()
        weather_layout = QVBoxLayout(weather_container)
        weather_layout.setContentsMargins(0, 0, 0, 0)
        weather_layout.setSpacing(0)
        
        weather_top = QWidget()
        weather_top_layout = QHBoxLayout(weather_top)
        weather_top_layout.setContentsMargins(0, 0, 0, 0)
        weather_top_layout.setSpacing(5)
        weather_top_layout.addWidget(self.weather_icon)
        weather_top_layout.addWidget(self.temp)
        
        weather_layout.addWidget(weather_top)
        weather_layout.addWidget(self.day)
        
        # Add to main layout
        self.layout.addWidget(time_container)
        self.layout.addWidget(weather_container)
        
        # Update time and date
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()
    
    def update_time(self):
        now = datetime.now()
        self.time.setText(now.strftime("%H:%M"))
        self.date.setText(now.strftime("%d/%m/%Y"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("piton2")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create stacked widget for side menus
        self.side_menu_stack = QStackedWidget()
        
        # Create different menus for each button
        self.side_menus = {}
        icon_names = ["settings", "usb", "equalizer", "volume", "pen", "camera", "wifi", "location", "next"]
        for name in icon_names:
            menu = SideMenu(name, self)
            self.side_menu_stack.addWidget(menu)
            self.side_menus[name] = menu
        
        # Add dynamic island at top right
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.addStretch(1)
        
        self.island = DynamicIsland()
        self.top_layout.addWidget(self.island)
        self.content_layout.addLayout(self.top_layout)

        # Sensor grid
        sensor_container = QWidget()
        sensor_grid = QGridLayout(sensor_container)
        sensor_grid.setContentsMargins(0, 0, 0, 0)
        sensor_grid.setSpacing(15)

        # Create sensor panels
        self.camera_panel = SensorPanel("CAMERA")
        self.heat_sensor_panel = SensorPanel("HEAT SENSOR")
        self.ai_panel = SensorPanel("AI SYSTEM OUTPUT")
        self.sonar_panel = SensorPanel("SONAR SENSOR VIRTUALIZER")
        self.surveillance_panel = SensorPanel("SURVEILLANCE CAM")
        self.tag_panel = SensorPanel("TAG SCANNER")

        # Add to grid with equal column weights
        sensor_grid.addWidget(self.camera_panel, 0, 0)
        sensor_grid.addWidget(self.sonar_panel, 0, 1)
        sensor_grid.addWidget(self.heat_sensor_panel, 1, 0)
        sensor_grid.addWidget(self.surveillance_panel, 1, 1)
        sensor_grid.addWidget(self.ai_panel, 2, 0)
        sensor_grid.addWidget(self.tag_panel, 2, 1)

        sensor_grid.setColumnStretch(0, 1)
        sensor_grid.setColumnStretch(1, 1)

        self.content_layout.addWidget(sensor_container, 1)

        # Bottom toolbar
        self.toolbar = BottomToolbar()
        self.content_layout.addWidget(self.toolbar)

        # S.A.R SYSTEM label
        self.sar_label = QLabel("S.A.R SYSTEM")
        self.sar_label.setStyleSheet("color: rgba(255, 255, 255, 150); font-size: 14px; font-weight: bold;")
        self.sar_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.sar_label.setContentsMargins(0, 0, 20, 10)
        self.content_layout.addWidget(self.sar_label)
        
        # Add to main layout
        self.main_layout.addWidget(self.side_menu_stack)
        self.main_layout.addWidget(self.content_widget)

        # Background effects (particles and light beam)
        import math  # Import math module for sin function
        self.bg_effects = BackgroundEffects(self.central_widget)
        self.bg_effects.resize(self.size())

        # Connect toolbar button signals
        for btn in self.toolbar.buttons:
            btn.clicked.connect(self.handle_toolbar_button)

        # Connect side menu exit buttons
        for menu in self.side_menus.values():
            menu.exit_btn.clicked.connect(self.close_all_menus)

        # Setup demo timer for random sensor activation
        self.demo_timer = QTimer(self)
        self.demo_timer.timeout.connect(self.demo_activate_random_sensor)
        self.demo_timer.start(3000)

        # Set dark background
        self.setStyleSheet("QMainWindow { background-color: #080a0e; }")
        
        # Current active menu
        self.active_menu = None

    def resizeEvent(self, event):
        self.bg_effects.resize(self.size())
        super().resizeEvent(event)

    def handle_toolbar_button(self):
        sender = self.sender()
        icon_name = sender.property("icon_name")
        
        if icon_name == "exit":
            self.close()
        elif icon_name in self.side_menus:
            self.toggle_menu(icon_name)
        elif icon_name == "camera":
            self.toggle_camera_panels()
        elif icon_name == "wifi":
            self.toggle_network_panels()
    
    def toggle_menu(self, menu_name):
        # If there's an active menu and it's not the one clicked
        if self.active_menu and self.active_menu != menu_name:
            self.side_menus[self.active_menu].toggle()  # Close active menu
        
        # Toggle the clicked menu
        menu = self.side_menus[menu_name]
        self.side_menu_stack.setCurrentWidget(menu)
        menu.toggle()
        
        # Update active menu reference
        if not menu.is_open:
            self.active_menu = None
        else:
            self.active_menu = menu_name
    
    def close_all_menus(self):
        # Close any open menu
        if self.active_menu:
            self.side_menus[self.active_menu].toggle()
            self.active_menu = None
    
    def toggle_camera_panels(self):
        self.camera_panel.set_active(not self.camera_panel.active)
        self.surveillance_panel.set_active(not self.surveillance_panel.active)
    
    def toggle_network_panels(self):
        self.sonar_panel.set_active(not self.sonar_panel.active)
        self.tag_panel.set_active(not self.tag_panel.active)

    def demo_activate_random_sensor(self):
        sensors = [
            self.camera_panel, self.heat_sensor_panel, self.ai_panel,
            self.sonar_panel, self.surveillance_panel, self.tag_panel
        ]
        for sensor in sensors:
            if random.random() < 0.2:
                sensor.set_active(not sensor.active)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())