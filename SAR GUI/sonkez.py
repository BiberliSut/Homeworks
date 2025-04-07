import sys
import random
import time
from datetime import datetime
from pathlib import Path
import json
import threading

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                              QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton)
from PySide6.QtCore import (Qt, QTimer, QPropertyAnimation, QRect, QSize, 
                           QEasingCurve, QPoint, Slot, QThread, Signal, QObject)
from PySide6.QtGui import (QColor, QPainter, QPen, QBrush, QFont, 
                          QFontMetrics, QGradient, QLinearGradient, QRadialGradient, 
                          QPainterPath, QPixmap, QIcon)

class ParticleEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")
        
        # Particle properties
        self.particles = []
        self.max_particles = 100
        for _ in range(self.max_particles):
            self.particles.append({
                'x': random.randint(0, self.width()),
                'y': random.randint(0, self.height()),
                'size': random.randint(2, 10),
                'speed': random.uniform(0.1, 0.5),
                'opacity': random.uniform(0.1, 0.6)
            })
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(30)  # Update every 30ms
    
    def update_particles(self):
        for particle in self.particles:
            # Move particles
            particle['y'] += particle['speed']
            
            # Reset particles that go off screen
            if particle['y'] > self.height():
                particle['y'] = -particle['size']
                particle['x'] = random.randint(0, self.width())
                particle['size'] = random.randint(2, 10)
                particle['speed'] = random.uniform(0.1, 0.5)
                particle['opacity'] = random.uniform(0.1, 0.6)
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw dark gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(20, 20, 40))
        gradient.setColorAt(1, QColor(10, 10, 20))
        painter.fillRect(self.rect(), gradient)
        
        # Draw particles
        for particle in self.particles:
            color = QColor(255, 255, 255, int(255 * particle['opacity']))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(particle['x']), 
                int(particle['y']), 
                particle['size'], 
                particle['size']
            )

class SignalStrengthIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.signal_level = 0  # 0 to 3 (no signal to full signal)
    
    def set_signal_level(self, level):
        self.signal_level = max(0, min(3, level))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw signal bars
        pen = QPen(QColor(150, 150, 150))
        pen.setWidth(2)
        painter.setPen(pen)
        
        bar_width = 4
        bar_spacing = 3
        total_width = (bar_width * 3) + (bar_spacing * 2)
        
        start_x = (self.width() - total_width) // 2
        base_y = self.height() - 10
        
        # Draw outline of all bars
        heights = [10, 15, 20]
        for i in range(3):
            x = start_x + i * (bar_width + bar_spacing)
            height = heights[i]
            painter.drawRect(x, base_y - height, bar_width, height)
        
        # Fill in active bars
        for i in range(self.signal_level):
            painter.fillRect(
                start_x + i * (bar_width + bar_spacing),
                base_y - heights[i],
                bar_width,
                heights[i],
                QColor(200, 200, 200)
            )

class SensorTile(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.has_signal = False
        self.signal_strength = 0
        
        self.setFixedSize(200, 140)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignCenter)
        
        # Signal strength indicator
        self.signal_indicator = SignalStrengthIndicator()
        layout.addWidget(self.signal_indicator, 0, Qt.AlignCenter)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #AAAAAA; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Status label
        self.status_label = QLabel("NO SIGNAL")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Timer for signal animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_signal)
        self.timer.start(1000)  # Check signal every second
    
    def animate_signal(self):
        # Randomly simulate signal status changes
        if random.random() < 0.1:  # 10% chance to change signal status
            self.has_signal = not self.has_signal
            
        if self.has_signal:
            self.signal_strength = min(3, self.signal_strength + 1)
            self.status_label.setText("SIGNAL OK")
            self.status_label.setStyleSheet("color: #88FF88; font-size: 12px;")
        else:
            self.signal_strength = max(0, self.signal_strength - 1)
            self.status_label.setText("NO SIGNAL")
            self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
            
        self.signal_indicator.set_signal_level(self.signal_strength)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 20, 20)
        painter.fillPath(path, QColor(0, 0, 0, 220))
        
        # Draw subtle border
        painter.setPen(QPen(QColor(50, 50, 50, 100), 1))
        painter.drawPath(path)

class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(250, 50)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Time and date
        time_date_layout = QVBoxLayout()
        
        self.time_label = QLabel("20:17")
        self.time_label.setStyleSheet("color: #EEEEEE; font-size: 18px; font-weight: bold;")
        time_date_layout.addWidget(self.time_label)
        
        self.date_label = QLabel("11/03/2025")
        self.date_label.setStyleSheet("color: #EEEEEE; font-size: 12px;")
        time_date_layout.addWidget(self.date_label)
        
        layout.addLayout(time_date_layout)
        
        # Weather icon
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(32, 32)
        self.weather_icon.setStyleSheet("color: #EEEEEE;")
        self.weather_icon.setText("☀️")
        self.weather_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.weather_icon)
        
        # Temperature and day
        temp_day_layout = QVBoxLayout()
        
        self.temp_label = QLabel("25°C")
        self.temp_label.setStyleSheet("color: #EEEEEE; font-size: 18px; font-weight: bold;")
        temp_day_layout.addWidget(self.temp_label)
        
        self.day_label = QLabel("Tuesday")
        self.day_label.setStyleSheet("color: #EEEEEE; font-size: 12px;")
        temp_day_layout.addWidget(self.day_label)
        
        layout.addLayout(temp_day_layout)
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(60000)  # Update every minute
        
        # Set initial data
        self.update_weather()
    
    def update_weather(self):
        # In a real app, you would fetch weather data from an API
        # For now, we'll just update the time and date
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%d/%m/%Y"))
        self.day_label.setText(now.strftime("%A"))
        
        # Simulate weather data
        temp = random.randint(20, 30)
        self.temp_label.setText(f"{temp}°C")
        
        # Random weather icons
        icons = ["☀️", "🌤️", "⛅", "🌥️", "☁️", "🌦️", "🌧️"]
        self.weather_icon.setText(random.choice(icons))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 25, 25)
        painter.fillPath(path, QColor(200, 200, 200, 180))

class SideMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 50, 10, 10)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("AYARLAR")
        title.setStyleSheet("color: #333333; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Menu items (placeholder gray rectangles)
        for _ in range(3):
            menu_item = QWidget()
            menu_item.setFixedHeight(60)
            menu_item.setStyleSheet("background-color: #DDDDDD; border-radius: 10px;")
            layout.addWidget(menu_item)
        
        layout.addStretch()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 20, 20)
        painter.fillPath(path, QColor(240, 240, 240, 220))

class BottomBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Icons
        icons = ["⚙️", "🔌", "🎛️", "🔊", "🎯", "📹", "⏩", "📡", "📍", "➡️"]
        for icon in icons:
            btn = QPushButton(icon)
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 30);
                    border-radius: 16px;
                }
            """)
            layout.addWidget(btn)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 30, 30)
        painter.fillPath(path, QColor(200, 200, 200, 180))

class SARBadge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 50)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Badge label
        label = QLabel("S.A.R SYSTEM")
        label.setStyleSheet("color: #EEEEEE; font-size: 12px; font-weight: bold;")
        layout.addWidget(label)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw hexagon shape
        path = QPainterPath()
        w, h = self.width(), self.height()
        path.moveTo(w * 0.2, 0)
        path.lineTo(w * 0.8, 0)
        path.lineTo(w, h * 0.5)
        path.lineTo(w * 0.8, h)
        path.lineTo(w * 0.2, h)
        path.lineTo(0, h * 0.5)
        path.closeSubpath()
        
        # Fill with gradient
        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0, QColor(100, 100, 100, 200))
        gradient.setColorAt(1, QColor(150, 150, 150, 200))
        painter.fillPath(path, gradient)
        
        # Draw border
        painter.setPen(QPen(QColor(180, 180, 180, 100), 1))
        painter.drawPath(path)

class SensorDataCollector(QObject):
    data_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.data = {
            "camera": {"status": "disconnected", "signal": 0},
            "heat_sensor": {"status": "disconnected", "signal": 0},
            "ai_system": {"status": "disconnected", "signal": 0},
            "sonar": {"status": "disconnected", "signal": 0},
            "surveillance": {"status": "disconnected", "signal": 0},
            "tag_scanner": {"status": "disconnected", "signal": 0},
        }
        
        # Start data collection thread
        self.thread = threading.Thread(target=self.collect_data)
        self.thread.daemon = True
        self.thread.start()
    
    def collect_data(self):
        while self.running:
            # Simulate random sensor status changes
            for sensor in self.data:
                if random.random() < 0.1:  # 10% chance to change status
                    if self.data[sensor]["status"] == "connected":
                        self.data[sensor]["status"] = "disconnected"
                        self.data[sensor]["signal"] = 0
                    else:
                        self.data[sensor]["status"] = "connected"
                        self.data[sensor]["signal"] = random.randint(1, 3)
            
            # Emit signal with new data
            self.data_changed.emit(self.data.copy())
            
            # Wait before next update
            time.sleep(2)
    
    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S.A.R System")
        self.setMinimumSize(1000, 600)
        
        # Central widget with transparent background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Particle effect background
        self.particle_bg = ParticleEffect()
        self.main_layout.addWidget(self.particle_bg)
        
        # Weather widget (top right)
        self.weather_widget = WeatherWidget()
        self.weather_widget.setParent(self.central_widget)
        self.weather_widget.move(self.width() - self.weather_widget.width() - 20, 20)
        
        # Side menu (initially hidden)
        self.side_menu = SideMenu()
        self.side_menu.setParent(self.central_widget)
        self.side_menu.move(-self.side_menu.width(), 0)  # Hidden initially
        
        # Bottom bar
        self.bottom_bar = BottomBar()
        self.bottom_bar.setParent(self.central_widget)
        
        # S.A.R badge
        self.sar_badge = SARBadge()
        self.sar_badge.setParent(self.central_widget)
        
        # Grid layout for sensor tiles
        self.sensor_grid = QWidget()
        self.sensor_grid.setParent(self.central_widget)
        
        grid_layout = QGridLayout(self.sensor_grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(20)
        
        # Create sensor tiles
        self.tiles = {
            "camera": SensorTile("CAMERA"),
            "heat_sensor": SensorTile("HEAT SENSOR"),
            "ai_system": SensorTile("AI SYSTEM OUTPUT"),
            "sonar": SensorTile("SONAR SENSOR VIRTUALIZER"),
            "surveillance": SensorTile("SURVEILLANCE CAM"),
            "tag_scanner": SensorTile("TAG SCANNER"),
        }
        
        # Add tiles to grid
        grid_layout.addWidget(self.tiles["camera"], 0, 0)
        grid_layout.addWidget(self.tiles["heat_sensor"], 0, 1)
        grid_layout.addWidget(self.tiles["ai_system"], 0, 2)
        grid_layout.addWidget(self.tiles["sonar"], 1, 0)
        grid_layout.addWidget(self.tiles["surveillance"], 1, 1)
        grid_layout.addWidget(self.tiles["tag_scanner"], 1, 2)
        
        # Menu button
        self.menu_button = QPushButton("☰")
        self.menu_button.setParent(self.central_widget)
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.move(20, 20)
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 200, 200, 180);
                border-radius: 20px;
                font-size: 20px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 200);
            }
        """)
        self.menu_button.clicked.connect(self.toggle_menu)
        
        # Show everything
        self.menu_visible = False
        
        # Sensor data collector
        self.data_collector = SensorDataCollector()
        self.data_collector.data_changed.connect(self.update_sensor_data)
        
        # Resize event to position widgets correctly
        self.resizeEvent(None)
    
    def toggle_menu(self):
        self.menu_visible = not self.menu_visible
        
        # Create animation for side menu
        animation = QPropertyAnimation(self.side_menu, b"pos")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        if self.menu_visible:
            animation.setStartValue(QPoint(-self.side_menu.width(), 0))
            animation.setEndValue(QPoint(0, 0))
        else:
            animation.setStartValue(QPoint(0, 0))
            animation.setEndValue(QPoint(-self.side_menu.width(), 0))
        
        animation.start()
    
    @Slot(dict)
    def update_sensor_data(self, data):
        for sensor, info in data.items():
            if sensor in self.tiles:
                tile = self.tiles[sensor]
                tile.has_signal = (info["status"] == "connected")
                tile.signal_strength = info["signal"]
                tile.signal_indicator.set_signal_level(info["signal"])
                
                if tile.has_signal:
                    tile.status_label.setText("SIGNAL OK")
                    tile.status_label.setStyleSheet("color: #88FF88; font-size: 12px;")
                else:
                    tile.status_label.setText("NO SIGNAL")
                    tile.status_label.setStyleSheet("color: #888888; font-size: 12px;")
    
    def resizeEvent(self, event):
        # Position weather widget
        self.weather_widget.move(self.width() - self.weather_widget.width() - 20, 20)
        
        # Position sensor grid
        grid_width = 3 * 200 + 2 * 20  # 3 columns * tile width + spacing
        grid_height = 2 * 140 + 20  # 2 rows * tile height + spacing
        self.sensor_grid.setFixedSize(grid_width, grid_height)
        self.sensor_grid.move(
            (self.width() - grid_width) // 2,
            (self.height() - grid_height) // 2
        )
        
        # Position bottom bar
        self.bottom_bar.setFixedWidth(min(700, self.width() - 40))
        self.bottom_bar.move(
            (self.width() - self.bottom_bar.width()) // 2,
            self.height() - self.bottom_bar.height() - 20
        )
        
        # Position S.A.R badge
        self.sar_badge.move(
            self.width() - self.sar_badge.width() - 20,
            self.height() - self.sar_badge.height() - 20
        )
    
    def closeEvent(self, event):
        # Stop the data collector thread when closing the app
        self.data_collector.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()  # Use full screen for best effect
    sys.exit(app.exec())