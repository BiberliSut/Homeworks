import sys
import os
import time
from datetime import datetime
import random
from PySide6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer, 
                           QParallelAnimationGroup, QPoint, QRect, Property, QSize)
from PySide6.QtGui import (QFont, QPainter, QColor, QLinearGradient, QPen, 
                          QBrush, QPainterPath, QPixmap, QIcon, QImage, QFontDatabase)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QFrame, 
                              QGraphicsOpacityEffect, QSizePolicy, QStackedWidget)

# Constants
DARK_BG = QColor(10, 12, 16)
PANEL_BG = QColor(0, 0, 0, 180)
ACCENT_COLOR = QColor(0, 120, 212)
TEXT_COLOR = QColor(200, 200, 200)
HIGHLIGHT_COLOR = QColor(255, 255, 255)

class ParticleSystem(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, parent.width()),
                'y': random.randint(0, parent.height()),
                'size': random.randint(2, 6),
                'speed': random.uniform(0.2, 1.0),
                'opacity': random.uniform(0.1, 0.7)
            })
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(50)
    
    def update_particles(self):
        for p in self.particles:
            p['y'] += p['speed']
            if p['y'] > self.parent().height():
                p['y'] = 0
                p['x'] = random.randint(0, self.parent().width())
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for p in self.particles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, int(255 * p['opacity'])))
            painter.drawEllipse(p['x'], p['y'], p['size'], p['size'])


class SignalStrengthIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 20)
        self.signal_level = 0  # 0-3
        
        self.animation = QPropertyAnimation(self, b"signal_level")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(3)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self._signal_level = 0
        
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
        self.setObjectName("sensorPanel")
        self.setStyleSheet("#sensorPanel { background-color: rgba(0, 0, 0, 180); border-radius: 12px; }")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(5)
        
        self.signal_icon = SignalStrengthIcon()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: rgba(200, 200, 200, 255); font-size: 14px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.status_label = QLabel("NO SIGNAL")
        self.status_label.setStyleSheet("color: rgba(200, 200, 200, 255); font-size: 16px; font-weight: bold;")
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
            self.status_label.setStyleSheet("color: rgba(0, 255, 128, 255); font-size: 16px; font-weight: bold;")
        else:
            self.signal_icon.animation.setDirection(QPropertyAnimation.Backward)
            self.signal_icon.animation.start()
            self.status_label.setText("NO SIGNAL")
            self.status_label.setStyleSheet("color: rgba(200, 200, 200, 255); font-size: 16px; font-weight: bold;")


class BottomToolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bottomToolbar")
        self.setStyleSheet("#bottomToolbar { background-color: rgba(240, 240, 240, 220); border-radius: 20px; }")
        self.setFixedHeight(60)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 5, 15, 5)
        self.layout.setSpacing(15)
        
        # Create toolbar buttons
        self.buttons = []
        button_icons = [
            "settings", "usb", "equalizer", "volume", "pen", "camera", 
            "exit", "wifi", "location", "next"
        ]
        
        for icon_name in button_icons:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: #333;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 30);
                    border-radius: 15px;
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 0, 0, 60);
                }}
            """)
            
            # In a real app, you'd use actual icon files
            icon_text = {
                "settings": "⚙️", "usb": "🔌", "equalizer": "🎛️", 
                "volume": "🔊", "pen": "✏️", "camera": "📷",
                "exit": "⏏️", "wifi": "📶", "location": "📍", "next": "➡️"
            }
            
            # Here we're using emoji as placeholders - in your real app, replace with your custom icons
            btn.setText(icon_text[icon_name])
            btn.setProperty("icon_name", icon_name)
            
            self.buttons.append(btn)
            self.layout.addWidget(btn)


class SettingsPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPanel")
        self.setStyleSheet("#settingsPanel { background-color: rgba(240, 240, 240, 255); border-radius: 12px; }")
        
        # Fixed width for the panel, height will match parent
        self.setFixedWidth(250)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)
        
        # Panel title
        self.title = QLabel("AYARLAR")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.layout.addWidget(self.title)
        
        # Settings options (placeholders)
        for i in range(3):
            option = QFrame()
            option.setStyleSheet("background-color: rgba(220, 220, 220, 200); border-radius: 8px;")
            option.setFixedHeight(50)
            self.layout.addWidget(option)
        
        # Add stretch to push content to the top
        self.layout.addStretch()
        
        # Animation properties
        self._pos_x = -self.width()
        self.animation = QPropertyAnimation(self, b"pos_x")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def get_pos_x(self):
        return self._pos_x
    
    def set_pos_x(self, x):
        self._pos_x = x
        self.setGeometry(self._pos_x, 0, self.width(), self.parent().height())
    
    pos_x = Property(int, get_pos_x, set_pos_x)
    
    def show_panel(self):
        self.animation.setStartValue(self._pos_x)
        self.animation.setEndValue(0)
        self.animation.start()
    
    def hide_panel(self):
        self.animation.setStartValue(self._pos_x)
        self.animation.setEndValue(-self.width())
        self.animation.start()


class WeatherWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("weatherWidget")
        self.setStyleSheet("#weatherWidget { background-color: transparent; }")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(10)
        
        # Weather icon (sun icon as placeholder)
        self.icon = QLabel("☀️")
        self.icon.setStyleSheet("font-size: 24px;")
        
        # Temperature
        self.temp = QLabel("25°C")
        self.temp.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        # Day
        self.day = QLabel("Tuesday")
        self.day.setStyleSheet("color: white; font-size: 16px;")
        
        self.layout.addWidget(self.icon)
        self.layout.addWidget(self.temp)
        self.layout.addWidget(self.day)


class TimeWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("timeWidget")
        self.setStyleSheet("#timeWidget { background-color: transparent; }")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(0)
        
        # Time
        self.time = QLabel("20:17")
        self.time.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin: 0;")
        self.time.setAlignment(Qt.AlignCenter)
        
        # Date
        self.date = QLabel("11/03/2025")
        self.date.setStyleSheet("color: white; font-size: 14px; margin: 0;")
        self.date.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.time)
        self.layout.addWidget(self.date)
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
    
    def update_time(self):
        current = datetime.now()
        self.time.setText(current.strftime("%H:%M"))
        self.date.setText(current.strftime("%d/%m/%Y"))


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setStyleSheet("#statusBar { background-color: rgba(240, 240, 240, 220); border-radius: 20px; }")
        self.setFixedHeight(60)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 5, 15, 5)
        
        # Left side - Time
        self.time_widget = TimeWidget()
        
        # Right side - Weather
        self.weather_widget = WeatherWidget()
        
        # Add widgets with stretches to position them
        self.layout.addWidget(self.time_widget)
        self.layout.addStretch(1)  # Push time to left, weather to right
        self.layout.addWidget(self.weather_widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("emojili-ilk-versiyon-piton")
        self.resize(800, 600)
        
        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create container for content
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)
        
        # Add status bar at the top
        self.status_bar = StatusBar()
        self.content_layout.addWidget(self.status_bar)
        
        # Sensor grid container
        self.grid_container = QWidget()
        self.grid_layout = QHBoxLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(15)
        
        # Create left column (3 sensors)
        self.left_column = QVBoxLayout()
        self.left_column.setSpacing(15)
        
        self.camera_panel = SensorPanel("CAMERA")
        self.heat_sensor_panel = SensorPanel("HEAT SENSOR")
        self.ai_panel = SensorPanel("AI SYSTEM OUTPUT")
        
        self.left_column.addWidget(self.camera_panel)
        self.left_column.addWidget(self.heat_sensor_panel)
        self.left_column.addWidget(self.ai_panel)
        
        # Create right column (3 sensors)
        self.right_column = QVBoxLayout()
        self.right_column.setSpacing(15)
        
        self.sonar_panel = SensorPanel("SONAR SENSOR VIRTUALIZER")
        self.surveillance_panel = SensorPanel("SURVEILLANCE CAM")
        self.tag_panel = SensorPanel("TAG SCANNER")
        
        self.right_column.addWidget(self.sonar_panel)
        self.right_column.addWidget(self.surveillance_panel)
        self.right_column.addWidget(self.tag_panel)
        
        # Add columns to grid
        self.grid_layout.addLayout(self.left_column)
        self.grid_layout.addLayout(self.right_column)
        
        # Add grid to content layout
        self.content_layout.addWidget(self.grid_container)
        
        # Add toolbar at the bottom
        self.toolbar = BottomToolbar()
        self.content_layout.addWidget(self.toolbar)
        
        # Add settings panel (initially hidden)
        self.settings_panel = SettingsPanel(self.central_widget)
        
        # Add particle system (background effect)
        self.particles = ParticleSystem(self.central_widget)
        self.particles.resize(self.size())
        
        # Add content container to main layout
        self.main_layout.addWidget(self.content_container)
        
        # S.A.R. System label at bottom right
        self.sar_label = QLabel("S.A.R SYSTEM")
        self.sar_label.setStyleSheet("color: rgba(255, 255, 255, 150); font-size: 14px; font-weight: bold;")
        self.sar_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.sar_label.setContentsMargins(0, 0, 20, 10)
        self.main_layout.addWidget(self.sar_label)
        
        # Connect signals
        for button in self.toolbar.buttons:
            button.clicked.connect(self.handle_toolbar_button)
        
        # Demo effect: randomly activate sensors
        self.demo_timer = QTimer(self)
        self.demo_timer.timeout.connect(self.demo_activate_random_sensor)
        self.demo_timer.start(3000)  # Every 3 seconds
        
        # Set stylesheet for the whole window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0c10;
            }
        """)
    
    def resizeEvent(self, event):
        # Resize particle system to match window size
        if hasattr(self, 'particles'):
            self.particles.resize(self.size())
        super().resizeEvent(event)
    
    def handle_toolbar_button(self):
        sender = self.sender()
        icon_name = sender.property("icon_name")
        
        if icon_name == "settings":
            self.settings_panel.show_panel()
        
        # Add more button handlers as needed
    
    def demo_activate_random_sensor(self):
        # Randomly activate/deactivate sensors for demo purposes
        sensors = [
            self.camera_panel, self.heat_sensor_panel, self.ai_panel,
            self.sonar_panel, self.surveillance_panel, self.tag_panel
        ]
        
        for sensor in sensors:
            # 20% chance to toggle state
            if random.random() < 0.2:
                sensor.set_active(not sensor.active)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
