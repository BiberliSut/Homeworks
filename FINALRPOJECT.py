import sys
import subprocess
import importlib.util
import os
import time

def check_requirements_cli():
    """
    Komut satırında gereksinimleri kontrol eder ve eksik olanları yükler.
    QApplication sorunlarından kaçınmak için GUI kullanmayan versiyon.
    """
    required = ['PySide6', 'requests', 'opencv-python', 'tensorflow', 'numpy',
               'psutil', 'ctypes', 'pathlib', 'datetime', 'urllib3']
    
    print("=== Gereksinimler denetleniyor ===")
    
    for pkg in required:
        print(f"Denetleniyor: {pkg}...", end=" ")
        sys.stdout.flush()
        
        if importlib.util.find_spec(pkg) is None:
            print("Yükleniyor...")
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', pkg],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                print(f"{pkg} başarıyla yüklendi.")
            except Exception as e:
                print(f"HATA: {pkg} yüklenirken bir sorun oluştu!")
        else:
            print("Zaten yüklü.")
    
    print("=== Tüm gereksinimler denetlendi! ===")

def create_gui_script():
    """
    Ayrı bir Python betiği oluşturur ve çalıştırır.
    Bu, QApplication sorunlarını tamamen önler.
    """
    script_content = """
import sys
import time
import threading
from PySide6.QtCore import Qt, QTimer, Property, QPropertyAnimation, QEasingCurve, Signal, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont

class InstallationSignals(QObject):
    update_output = Signal(str)
    update_progress = Signal(float)
    finished = Signal()

class DynamicIslandWindow(QMainWindow):
    def __init__(self, packages):
        super().__init__()
        self.packages = packages
        
        # Pencere özelliklerini ayarla
        self.setWindowTitle("Yükleniyor...")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Sinyaller
        self.signals = InstallationSignals()
        self.signals.update_output.connect(self.update_message)
        self.signals.update_progress.connect(self.update_progress)
        self.signals.finished.connect(self.close)
        
        # Dynamic Island container
        self.island_widget = IslandWidget()
        self.layout.addWidget(self.island_widget)
        
        # Pencere boyutunu ayarla
        self.resize(380, 120)
        
        # Ekranın ortasına konumlandır
        self.center_on_screen()
        
        # Denetleme işlemini başlat
        QTimer.singleShot(100, self.start_checking)
    
    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def update_message(self, message):
        self.island_widget.set_message(message)
    
    def update_progress(self, value):
        self.island_widget.set_progress(value)
    
    def start_checking(self):
        self.thread = threading.Thread(target=self.process_requirements, daemon=True)
        self.thread.start()
    
    def process_requirements(self):
        import importlib.util
        import subprocess
        import sys
        import time
        
        for i, pkg in enumerate(self.packages):
            progress = (i / len(self.packages)) * 100
            self.signals.update_progress.emit(progress)
            self.signals.update_output.emit(f"Denetleniyor: {pkg}")
            
            # Biraz beklet UI'nin güncellenmesi için
            time.sleep(0.3)
            
            if importlib.util.find_spec(pkg) is None:
                self.signals.update_output.emit(f"{pkg} yükleniyor...")
                try:
                    # Yükleme işlemi
                    subprocess.check_call(
                        [sys.executable, '-m', 'pip', 'install', pkg],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                    )
                    self.signals.update_output.emit(f"{pkg} başarıyla yüklendi")
                except Exception as e:
                    self.signals.update_output.emit(f"Hata: {pkg} yüklenirken bir sorun oluştu")
            else:
                self.signals.update_output.emit(f"{pkg} zaten yüklü")
            
            time.sleep(0.5)
        
        # İşlem tamamlandı
        self.signals.update_progress.emit(100)
        self.signals.update_output.emit("Tüm gereksinimler denetlendi!")
        time.sleep(1)
        self.signals.finished.emit()

class IslandWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Özellikler
        self._progress = 0
        self._message = "Ön gereksinimler denetleniyor..."
        self._color = QColor(55, 55, 55)  # Koyu gri
        
        # Metin için label
        self.label = QLabel(self._message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-family: Arial; font-size: 16px; font-weight: bold;")
        
        # Label için layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Animasyon için özellikler
        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Minimum boyut belirle
        self.setMinimumSize(350, 80)
    
    def set_message(self, message):
        self._message = message
        self.label.setText(message)
        self.update()
    
    def set_progress(self, progress):
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(progress)
        self._animation.start()
    
    def get_progress(self):
        return self._progress
    
    def set_progress_direct(self, progress):
        self._progress = progress
        self.update()
    
    progress = Property(float, get_progress, set_progress_direct)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Yol oluştur
        path = QPainterPath()
        rect = self.rect()
        
        # Dynamic Island şekli (Oval)
        path.addRoundedRect(rect, 25, 25)
        
        # Arkaplan rengini ayarla
        painter.fillPath(path, self._color)
        
        # İlerleme çubuğu çiz
        if self._progress > 0:
            progress_width = rect.width() * (self._progress / 100)
            progress_rect = rect
            progress_rect.setWidth(progress_width)
            progress_path = QPainterPath()
            progress_path.addRoundedRect(progress_rect, 25, 25)
            painter.fillPath(progress_path, QColor(75, 75, 75))  # Biraz daha açık gri

if __name__ == "__main__":
    # Tüm paketleri burada listele
    packages = [
        'PySide6', 'requests', 'opencv-python', 'tensorflow', 'numpy', 
        'pathlib', 'datetime', 'psutil', 'ctypes', 'urllib3', 'math',
        'random', 'json'
    ]
    
    app = QApplication(sys.argv)
    window = DynamicIslandWindow(packages)
    window.show()
    app.exec()
    
    # QApplication tamamen sonlandığında exit koduyla çık
    sys.exit(0)
"""
    
    # Geçici betiği oluştur
    temp_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_requirements_checker.py")
    
    with open(temp_script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Betiği çalıştır ve tamamlanmasını bekle
    subprocess.call([sys.executable, temp_script_path])
    
    # Geçici betiği sil
    try:
        os.remove(temp_script_path)
    except:
        pass

def check_requirements():
    """
    Gereksinimleri kontrol et ve yükle.
    Temiz bir çözüm için GUI gereksinimlerini ayrı bir süreçte çalıştırır.
    """
    # İlk olarak PySide6 yüklü mü kontrol et, yoksa yükle
    if importlib.util.find_spec('PySide6') is None:
        print("PySide6 yükleniyor...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PySide6'])
    
    # GUI'yi ayrı süreçte çalıştır
    create_gui_script()

# Gereksinim kontrolü yapan fonksiyonu çağır
if __name__ == "__main__":
    check_requirements()
    
    # Buradan sonra ana program devam eder...






import sys
import random
import time
import math
from pathlib import Path
import json
import requests
from datetime import datetime
import threading
import resources_rc
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                              QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
                              QGraphicsBlurEffect)
from PySide6.QtCore import (Qt, QTimer, QPropertyAnimation, QRect, QSize, 
                           QEasingCurve, QPoint, Slot, QThread, Signal, QObject)
from PySide6.QtGui import (QColor, QPainter, QPen, QBrush, QFont, 
                          QFontMetrics, QGradient, QLinearGradient, QRadialGradient, 
                          QPainterPath, QPixmap, QIcon, QImage)
from PySide6.QtGui import QTransform
import cv2  # OpenCV kütüphanesini ekliyoruz
import tensorflow as tf
import numpy as np
import os
import urllib.request

class BackgroundEffects(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        self.particles = [{
            'x': random.randint(0, self.screen_width),
            'y': random.randint(0, self.screen_height),
            'size': random.randint(1, 18),  # Daha geniş boyut aralığı
            'speed_x': random.uniform(-0.5, 0.5),
            'speed_y': random.uniform(-0.5, 0.5),
            'opacity': random.uniform(0.2, 0.6),  # Opaklık değerlerini arttırdım
            'color': random.choice([
                QColor(255, 222, 173, int(255 * random.uniform(0.2, 0.5))),  # Opaklığı arttırdım
                QColor(238, 203, 173, int(255 * random.uniform(0.2, 0.5))),
                QColor(222, 184, 135, int(255 * random.uniform(0.2, 0.5))),
                QColor(245, 222, 179, int(255 * random.uniform(0.2, 0.5))),
                QColor(210, 180, 140, int(255 * random.uniform(0.2, 0.5)))
            ])
        } for _ in range(200)]  # Parçacık sayısını azalttım ancak çeşitli boyutlarda
        self.main_light_beam = {
            'origin_x': -200,  # Sol üst köşeden başlayıp dışarıdan gelecek
            'origin_y': -200,
            'angle': 30,  # Açısı
            'length': self.screen_width * 1.5,  # Uzunluğu
            'width_start': 400,  # Başlangıç genişliği
            'width_end': self.screen_width,  # Bitiş genişliği (This code is written by Erdem Erçetin genişleyen ışık)
            'opacity': 0.12,  # Sönük olması için düşük opaklık
            'color_start': QColor(255, 250, 240, 70),  # Başlangıç rengi (daha parlak)
            'color_end': QColor(255, 245, 230, 10),  # Bitiş rengi (sönük)
            'phase': 0,
            'speed': 0.02
        }
        self.secondary_beams = [{
            'origin_x': -100,
            'origin_y': -100, 
            'angle': 25 + i * 15,  # Farklı açılarda ışık demetleri
            'length': self.screen_width * random.uniform(0.8, 1.2),
            'width_start': 100 + i * 50,
            'width_end': 300 + i * 100,
            'opacity': 0.05 + 0.02 * i,
            'color_start': QColor(255, 250, 240, 40),
            'color_end': QColor(255, 245, 230, 5),
            'phase': random.uniform(0, 2 * math.pi),
            'speed': 0.01 + 0.005 * i
        } for i in range(4)]  # 4 farklı ikincil ışık demeti
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_effects)
        self.timer.start(30)
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(8)  # Bulanıklık miktarını artırdım
        self.setGraphicsEffect(self.blur_effect)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        for p in self.particles:
            p['x'] = random.randint(0, self.screen_width)
            p['y'] = random.randint(0, self.screen_height)
        self.main_light_beam['length'] = self.screen_width * 1.5
        self.main_light_beam['width_end'] = self.screen_width
        for beam in self.secondary_beams:
            beam['length'] = self.screen_width * random.uniform(0.8, 1.2)

    def update_effects(self):
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        for p in self.particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            if p['x'] < -p['size']:
                p['x'] = self.screen_width + p['size']
            elif p['x'] > self.screen_width + p['size']:
                p['x'] = -p['size']
                
            if p['y'] < -p['size']:
                p['y'] = self.screen_height + p['size']
            elif p['y'] > self.screen_height + p['size']:
                p['y'] = -p['size']
        self.main_light_beam['phase'] += self.main_light_beam['speed']
        pulse_factor = 0.15 * math.sin(self.main_light_beam['phase']) + 0.85  # Işık yanıp sönmesi
        self.main_light_beam['opacity'] = 0.12 * pulse_factor
        for beam in self.secondary_beams:
            beam['phase'] += beam['speed']
            beam_pulse = 0.2 * math.sin(beam['phase']) + 0.8
            beam['opacity'] = (0.05 + 0.02 * beam_pulse) * pulse_factor
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        screen_width = self.screen_width
        screen_height = self.screen_height
        gradient = QLinearGradient(0, 0, 0, screen_height)
        gradient.setColorAt(0, QColor(20, 20, 40))
        gradient.setColorAt(1, QColor(10, 10, 20))
        painter.fillRect(self.rect(), gradient)
        painter.save()
        transform = QTransform()
        transform.translate(self.main_light_beam['origin_x'], self.main_light_beam['origin_y'])
        transform.rotate(self.main_light_beam['angle'])
        painter.setTransform(transform)
        beam_gradient = QLinearGradient(0, 0, self.main_light_beam['length'], 0)
        start_color = self.main_light_beam['color_start']
        start_color.setAlpha(int(255 * self.main_light_beam['opacity']))
        end_color = self.main_light_beam['color_end']
        end_color.setAlpha(int(10 * self.main_light_beam['opacity']))
        
        beam_gradient.setColorAt(0, start_color)
        beam_gradient.setColorAt(1, end_color)
        beam_path = QPainterPath()
        beam_path.moveTo(0, 0)
        beam_path.lineTo(self.main_light_beam['length'], -self.main_light_beam['width_end'] / 2)
        beam_path.lineTo(self.main_light_beam['length'], self.main_light_beam['width_end'] / 2)
        beam_path.closeSubpath()
        
        painter.fillPath(beam_path, beam_gradient)
        painter.restore()
        for beam in self.secondary_beams:
            painter.save()
            transform = QTransform()
            transform.translate(beam['origin_x'], beam['origin_y'])
            transform.rotate(beam['angle'])
            painter.setTransform(transform)
            sec_beam_gradient = QLinearGradient(0, 0, beam['length'], 0)
            sec_start_color = beam['color_start']
            sec_start_color.setAlpha(int(255 * beam['opacity']))
            sec_end_color = beam['color_end']
            sec_end_color.setAlpha(int(5 * beam['opacity']))
            
            sec_beam_gradient.setColorAt(0, sec_start_color)
            sec_beam_gradient.setColorAt(1, sec_end_color)
            sec_beam_path = QPainterPath()
            sec_beam_path.moveTo(0, 0)
            sec_beam_path.lineTo(beam['length'], -beam['width_end'] / 2)
            sec_beam_path.lineTo(beam['length'], beam['width_end'] / 2)
            sec_beam_path.closeSubpath()
            
            painter.fillPath(sec_beam_path, sec_beam_gradient)
            painter.restore()
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        for p in self.particles:
            size_factor = p['size'] / 25.0
            opacity_factor = 0.3 + (size_factor * 0.7)  # Değerleri 0.3-1.0 arasında tutar
            particle_color = p['color']
            particle_color.setAlpha(int(255 * opacity_factor * p['opacity']))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(particle_color)
            particle_size = p['size'] * 1.2  # Boyutu %20 artır
            painter.drawEllipse(
                int(p['x'] - particle_size/2), 
                int(p['y'] - particle_size/2), 
                particle_size, 
                particle_size
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
        pen = QPen(QColor(150, 150, 150))
        pen.setWidth(2)
        painter.setPen(pen)
        
        bar_width = 4
        bar_spacing = 3
        total_width = (bar_width * 3) + (bar_spacing * 2)
        
        start_x = (self.width() - total_width) // 2
        base_y = self.height() - 10
        heights = [10, 15, 20]
        for i in range(3):
            x = start_x + i * (bar_width + bar_spacing)
            height = heights[i]
            painter.drawRect(x, base_y - height, bar_width, height)
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
        self.setFixedSize(450, 315)  # Ekranda düzgün görünmesi için boyutu ayarlandı
        self.title = title
        self.has_signal = False
        self.signal_strength = 0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)  # Margin'leri ayarladık
        layout.setAlignment(Qt.AlignCenter)
        self.signal_indicator = SignalStrengthIndicator()
        self.signal_indicator.setFixedSize(40, 40)  # Orijinal boyutunu koruduk Code Author Erdem Erçetin
        layout.addWidget(self.signal_indicator, 0, Qt.AlignCenter)
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #AAAAAA; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_label)
        self.status_label = QLabel("NO SIGNAL")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-size: 21px;")
        layout.addWidget(self.status_label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_signal)
        self.timer.start(1000)  # Check signal every second
    
    def animate_signal(self):
        if random.random() < 0.1:  # 10% chance to change signal status
            self.has_signal = not self.has_signal
            
        if self.has_signal:
            self.signal_strength = min(3, self.signal_strength + 1)
            self.status_label.setText("SIGNAL OK")
            self.status_label.setStyleSheet("color: #88FF88; font-size: 21px;")
        else:
            self.signal_strength = max(0, self.signal_strength - 1)
            self.status_label.setText("NO SIGNAL")
            self.status_label.setStyleSheet("color: #888888; font-size: 21px;")
            
        self.signal_indicator.set_signal_level(self.signal_strength)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 30, 30)
        painter.fillPath(path, QColor(0, 0, 0, 220))
        painter.setPen(QPen(QColor(50, 50, 50, 100), 1))
        painter.drawPath(path)

class WebcamWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(450, 315)
        self.has_camera = self.check_camera()
        self.has_signal = False
        self.signal_strength = 0

        if self.has_camera:
            self.model_path = "movenet_thunder.tflite"
            if not os.path.exists(self.model_path):
                url = "https://tfhub.dev/google/lite-model/movenet/singlepose/thunder/tflite/4?lite-format=tflite"
                urllib.request.urlretrieve(url, self.model_path)
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.BODY_PART_MAPPING = {
                'nose': 'BURUN', 'left_eye': 'GOZLER', 'right_eye': 'GOZLER',
                'left_ear': 'KULAK', 'right_ear': 'KULAK',
                'left_shoulder': 'OMUZ', 'right_shoulder': 'OMUZ',
                'left_elbow': 'DIRSEK', 'right_elbow': 'DIRSEK',
                'left_wrist': 'EL', 'right_wrist': 'EL',
                'left_hip': 'KALCA', 'right_hip': 'KALCA',
                'left_knee': 'DIZ', 'right_knee': 'DIZ',
                'left_ankle': 'AYAK', 'right_ankle': 'AYAK'
            }
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
        else:
            # Kamera yoksa SensorTile benzeri görünüm
            layout = QVBoxLayout(self)
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setAlignment(Qt.AlignCenter)
            
            self.signal_indicator = SignalStrengthIndicator()
            self.signal_indicator.setFixedSize(40, 40)
            layout.addWidget(self.signal_indicator, 0, Qt.AlignCenter)
            
            self.title_label = QLabel("WEBCAM")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setStyleSheet("color: #AAAAAA; font-size: 24px; font-weight: bold;")
            layout.addWidget(self.title_label)
            
            self.status_label = QLabel("NO SIGNAL")
            self.status_label.setAlignment(Qt.AlignCenter)
            self.status_label.setStyleSheet("color: #888888; font-size: 21px;")
            layout.addWidget(self.status_label)

        self.current_frame = None

    def check_camera(self):
        cap = cv2.VideoCapture(0)
        if cap is None or not cap.isOpened():
            if cap is not None:
                cap.release()
            return False
        cap.release()
        return True

    def process_image(self, image):
        input_shape = self.input_details[0]['shape'][1:3]
        input_dtype = self.input_details[0]['dtype']
        img = cv2.resize(image, (input_shape[1], input_shape[0]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if input_dtype == np.uint8:
            img = np.expand_dims(img, axis=0)
        else:
            img = (np.expand_dims(img, axis=0).astype(np.float32) / 255.0)
        
        return img

    def create_body_part_bounding_boxes(self, keypoints, confidence_threshold=0.3):
        body_parts = {}
        valid_keypoints = {}
        
        for idx, (y, x, confidence) in enumerate(keypoints):
            if confidence > confidence_threshold:
                keypoint_name = list(self.BODY_PART_MAPPING.keys())[idx % len(self.BODY_PART_MAPPING)]
                body_part = self.BODY_PART_MAPPING[keypoint_name]
                
                if body_part not in valid_keypoints:
                    valid_keypoints[body_part] = []
                valid_keypoints[body_part].append((y, x))
        bounding_boxes = {}
        padding = 0.05
        for part, points in valid_keypoints.items():
            if points:
                y_coords = [p[0] for p in points]
                x_coords = [p[1] for p in points]
                
                y_min = max(0, min(y_coords) - padding)
                x_min = max(0, min(x_coords) - padding)
                y_max = min(1, max(y_coords) + padding)
                x_max = min(1, max(x_coords) + padding)
                
                bounding_boxes[part] = (y_min, x_min, y_max, x_max)
        
        return bounding_boxes

    def draw_bounding_boxes(self, image, keypoints):
        h, w, _ = image.shape
        bounding_boxes = self.create_body_part_bounding_boxes(keypoints)
        box_color = (200, 200, 200)  # Beyaz
        
        for part, (y_min, x_min, y_max, x_max) in bounding_boxes.items():
            x_min_px, y_min_px = int(x_min * w), int(y_min * h)
            x_max_px, y_max_px = int(x_max * w), int(y_max * h)
            cv2.rectangle(image, (x_min_px, y_min_px), (x_max_px, y_max_px), box_color, 1)  # İnce çerçeve
            text = part
            font_scale = 0.4  # Yazı boyutunu küçült (0.7'den 0.4'e)
            thickness = 1     # Yazı kalınlığını azalt (2'den 1'e)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            bg_padding = 2  # Padding'i azalt
            cv2.rectangle(image, 
                         (x_min_px, y_min_px - text_size[1] - bg_padding * 2),
                         (x_min_px + text_size[0], y_min_px),
                         (0, 0, 0, 150), -1)  # Yarı saydam arka plan
            cv2.putText(image, text, 
                       (x_min_px, y_min_px - bg_padding),  # Metni biraz yukarı kaydır
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, (255, 255, 255), 
                       thickness, 
                       cv2.LINE_AA)
        
        return image

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.width(), self.height()))
                input_image = self.process_image(frame)
                self.interpreter.set_tensor(self.input_details[0]['index'], input_image)
                self.interpreter.invoke()
                keypoints = self.interpreter.get_tensor(self.output_details[0]['index'])[0, 0, :, :]
                self.current_frame = self.draw_bounding_boxes(frame, keypoints)
                self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 30, 30)

        if not self.has_camera:
            # Kamera yoksa siyah arka plan
            painter.fillPath(path, QColor(0, 0, 0, 220))
            painter.setPen(QPen(QColor(50, 50, 50, 100), 1))
            painter.drawPath(path)
            return

        # Kamera varsa normal görüntüleme
        painter.setClipPath(path)
        if self.current_frame is not None:
            h, w, ch = self.current_frame.shape
            bytes_per_line = ch * w
            image = QImage(self.current_frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        painter.setPen(QPen(QColor(50, 50, 50, 150), 2))
        painter.drawPath(path)

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)

class ESP32CamTile(SensorTile):
    def __init__(self, title, esp32_url, parent=None):
        super().__init__(title, parent)
        self.esp32_url = esp32_url  # ESP32-CAM'in URL'si
        self.current_frame = None  # ESP32-CAM'den alınan son kareyi saklamak için
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  # 100 ms'de bir kare güncelle

    def update_frame(self):
        try:
            response = requests.get(self.esp32_url, timeout=2)
            if response.status_code == 200:
                image_data = response.content
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                self.current_frame = pixmap
                self.has_signal = True
                self.status_label.setText("SIGNAL OK")
                self.status_label.setStyleSheet("color: #88FF88; font-size: 21px;")
            else:
                raise Exception("ESP32-CAM bağlantı hatası")
        except Exception as e:
            self.current_frame = None
            self.has_signal = False
            self.status_label.setText("NO SIGNAL")
            self.status_label.setStyleSheet("color: #FF8888; font-size: 21px;")
            print(f"ESP32-CAM Hatası: {e}")
        self.update()  # paintEvent'i tetikle

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 30, 30)
        painter.fillPath(path, QColor(0, 0, 0, 220))  # Siyah arka plan
        if self.current_frame is not None:
            clip_path = QPainterPath()
            clip_path.addRoundedRect(self.rect(), 30, 30)
            painter.setClipPath(clip_path)
            scaled_pixmap = self.current_frame.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(self.rect(), scaled_pixmap)
        painter.setPen(QPen(QColor(50, 50, 50, 150), 2))
        painter.drawPath(path)

class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 70)
        self.icons_dir = Path(__file__).parent / "icons"
        self.weather_icons = {
            "Sunny": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/sunny.png",
            "Clear": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/sunny.png",
            "Partly cloudy": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/partly_cloudy.png",
            "Cloudy": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/cloudy.png",
            "Overcast": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/cloudy.png",
            "Mist": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/cloudy.png",
            "Patchy rain possible": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/rainy.png",
            "Light rain": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/rainy.png",
            "Moderate rain": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/rainy.png",
            "Heavy rain": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/rainy.png",
            "Light snow": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/snowy.png",
            "Moderate snow": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/snowy.png",
            "Heavy snow": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/snowy.png",
            "Thunderstorm": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/stormy.png",
            "Thunder": "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/stormy.png"
        }
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(0)
        time_date_layout = QVBoxLayout()
        
        self.time_label = QLabel("15:50")
        self.time_label.setStyleSheet("color: #333333; font-size: 20px; font-weight: bold;")
        time_date_layout.addWidget(self.time_label)
        
        self.date_label = QLabel("10/04/2025")
        self.date_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        time_date_layout.addWidget(self.date_label)
        
        layout.addLayout(time_date_layout)
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(70, 70)
        self.weather_icon.setContentsMargins(0, -10, 0, 0)
        layout.addWidget(self.weather_icon)
        temp_day_layout = QVBoxLayout()
        temp_day_layout.setContentsMargins(10, 0, 0, 0)  # Sol tarafa boşluk ekleyerek ikona yaklaştırıyoruz
        
        self.temp_label = QLabel("25°C")
        self.temp_label.setStyleSheet("color: #333333; font-size: 20px; font-weight: bold;")
        temp_day_layout.addWidget(self.temp_label)
        
        self.day_label = QLabel("PERŞEMBE")
        self.day_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        temp_day_layout.addWidget(self.day_label)
        
        layout.addLayout(temp_day_layout)
        layout.setStretch(0, 2)  # Zaman-tarih kısmına daha az yer
        layout.setStretch(1, 3)  # İkona daha fazla yer
        layout.setStretch(2, 2)  # Sıcaklık-gün kısmına daha az yer
        self.set_default_icon()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(300000)  # Her 5 dakikada bir güncelle
        self.update_weather()
    
    def set_default_icon(self):
        """Varsayılan ikonu yükle"""
        try:
            icon_path = "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/partly_cloudy.png"
            pixmap = QPixmap(icon_path)
            if pixmap.isNull():
                icon_path = str(self.icons_dir / "partly_cloudy.png")
                pixmap = QPixmap(icon_path)
                
            if not pixmap.isNull():
                self.weather_icon.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                print(f"Ikon yüklenemedi: {icon_path}")
        except Exception as e:
            print(f"İkon yükleme hatası: {e}")
    
    def get_weather_data(self, city="Istanbul"):
        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Hava durumu API hatası: {e}")
            return None
    
    def get_icon_path(self, condition):
        """Hava durumuna göre uygun ikon yolunu al"""
        for key in self.weather_icons:
            if key.lower() in condition.lower():
                return f":/icons/icons/{self.weather_icons[key]}"
        return "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/partly_cloudy.png"
    
    def update_weather(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%d/%m/%Y"))
        turkish_days = {
            "Monday": "PAZARTESİ",
            "Tuesday": "SALI",
            "Wednesday": "ÇARŞAMBA",
            "Thursday": "PERŞEMBE",
            "Friday": "CUMA",
            "Saturday": "CUMARTESİ",
            "Sunday": "PAZAR"
        }
        
        day_english = now.strftime("%A")
        day_turkish = turkish_days.get(day_english, day_english.upper())
        self.day_label.setText(day_turkish)
        weather_data = self.get_weather_data()
        
        if weather_data:
            try:
                temp = weather_data["current_condition"][0]["temp_C"]
                condition = weather_data["current_condition"][0]["weatherDesc"][0]["value"]
                self.temp_label.setText(f"{temp}°C")
                try:
                    icon_path = self.get_icon_path(condition)
                    pixmap = QPixmap(icon_path)
                    
                    if pixmap.isNull():
                        for key in self.weather_icons:
                            if key.lower() in condition.lower():
                                file_path = str(self.icons_dir / self.weather_icons[key])
                                pixmap = QPixmap(file_path)
                                if not pixmap.isNull():
                                    break
                    
                    if not pixmap.isNull():
                        self.weather_icon.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    else:
                        self.set_default_icon()
                        
                except Exception as e:
                    print(f"İkon yükleme hatası: {e}")
                    self.set_default_icon()
                    
            except Exception as e:
                print(f"Hava durumu veri işleme hatası: {e}")
                self.set_default_icon()
        else:
            self.set_default_icon()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 35, 35)
        painter.fillPath(path, QColor(240, 240, 240, 240))
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        painter.drawPath(path) # Slightly darker and less transparent # Slightly darker and less transparent # Slightly darker and less transparent

class SideMenu(QWidget):
    def __init__(self, menu_type="AYARLAR", parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)  # Menüyü daha geniş yapma
        self.menu_type = menu_type
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 50, 20, 20)
        self.layout.setSpacing(25)
        self.title_label = QLabel(menu_type)
        self.title_label.setStyleSheet("color: #333333; font-size: 22px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        if menu_type == "AYARLAR":
            self.battery_info = self.get_battery_info()
            self.battery_label = QLabel(self.battery_info)
            self.battery_label.setStyleSheet("color: #555555; font-size: 16px; font-weight: bold; margin-left: 10px;")
            self.layout.addWidget(self.battery_label)
            self.battery_timer = QTimer(self)
            self.battery_timer.timeout.connect(self.update_battery_info)
            self.battery_timer.start(60000)  # Her dakika güncelle
        self.create_menu_items()
        self.layout.addStretch()
    
    def get_battery_info(self):
        """Sistem pil bilgisini alır"""
        try:
            import psutil
            battery = psutil.sensors_battery()
            
            if battery:
                percent = battery.percent
                plugged = battery.power_plugged
                
                if plugged:
                    return f"🔌 Güç Kaynağına Bağlı ({percent}%)"
                else:
                    return f"🔋 Pil Durumu: {percent}%"
            else:
                return "🔌 Güç Kaynağına Bağlı"
                
        except (ImportError, AttributeError):
            import sys
            if sys.platform == 'win32':
                import ctypes
                status = ctypes.windll.kernel32.GetSystemPowerStatus
                status.restype = ctypes.c_int
                status.argtypes = [ctypes.POINTER(ctypes.c_byte)]
                buffer = (ctypes.c_byte * 12)()
                if status(buffer):
                    ac_status = buffer[0]
                    battery_flag = buffer[1]
                    battery_life = buffer[2]
                    
                    if ac_status == 1:
                        return "🔌 Güç Kaynağına Bağlı"
                    elif battery_life < 255:  # 255 bilinmeyen değer
                        return f"🔋 Pil Durumu: {battery_life}%"
                
            return "🔌 Güç Kaynağına Bağlı"  # Varsayılan olarak
    
    def update_battery_info(self):
        """Pil bilgisini günceller"""
        if self.menu_type == "AYARLAR" and hasattr(self, 'battery_label'):
            self.battery_info = self.get_battery_info()
            self.battery_label.setText(self.battery_info)
    
    def create_menu_items(self):
        """Menü tipine göre butonları oluşturur"""
        for i in reversed(range(2 if self.menu_type == "AYARLAR" else 1, self.layout.count())):
            item = self.layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        menu_buttons = self.get_menu_buttons(self.menu_type)
        
        for button_info in menu_buttons:
            menu_item = QPushButton(f"{button_info['emoji']} {button_info['text']}")
            menu_item.setFixedHeight(60)
            menu_item.setStyleSheet("""
                QPushButton {
                    background-color: #EEEEEE; 
                    border-radius: 10px;
                    color: #333333;
                    font-size: 16px;
                    font-weight: bold;  /* Yazıları bold yaptık */
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover {
                    background-color: #DDDDDD;
                }
            """)
            self.layout.addWidget(menu_item)

    def get_menu_buttons(self, menu_type):
        """Her menü tipi için özel butonları döndürür"""
        menu_buttons = {
            "AYARLAR": [
                {"text": "Ekran Ayarları", "emoji": "🖥️"},
                {"text": "Sistem Bilgisi", "emoji": "ℹ️"}
            ],
            "BAĞLANTILAR": [
                {"text": "Bluetooth", "emoji": "📶"},
                {"text": "WiFi Ağları", "emoji": "📡"},
                {"text": "Cihaz Eşleştirme", "emoji": "🔄"}
            ],
            "KONTROLLER": [
                {"text": "Joystick Ayarları", "emoji": "🕹️"},
                {"text": "Tuş Atamaları", "emoji": "⌨️"},
                {"text": "Hassasiyet Ayarları", "emoji": "📊"}
            ],
            "SES AYARLARI": [
                {"text": "Ses Seviyesi", "emoji": "🔊"},
                {"text": "Bildirim Sesleri", "emoji": "🔔"},
                {"text": "Mikrofon Ayarları", "emoji": "🎙️"}
            ],
            "HEDEF AYARLARI": [
                {"text": "Hedef Tespiti", "emoji": "🎯"},
                {"text": "Takip Modu", "emoji": "👁️"},
                {"text": "Hassasiyet Ayarları", "emoji": "⚙️"}
            ],
            "KAMERA AYARLARI": [
                {"text": "Zoom Ayarları", "emoji": "🔍"},
                {"text": "Kayıt Kalitesi", "emoji": "📹"},
                {"text": "Görüş Modu", "emoji": "👁️"}
            ],
            "İLERİ AYARLAR": [
                {"text": "Gelişmiş Kontroller", "emoji": "⚙️"},
                {"text": "Yazılım Güncelleme", "emoji": "🔄"},
                {"text": "Fabrika Ayarları", "emoji": "🔧"}
            ],
            "UYDU AYARLARI": [
                {"text": "GPS Bağlantısı", "emoji": "🛰️"},
                {"text": "Konum Servisleri", "emoji": "📍"},
                {"text": "Harita Ayarları", "emoji": "🗺️"}
            ],
            "KONUM AYARLARI": [
                {"text": "Navigasyon", "emoji": "🧭"},
                {"text": "Koordinat Sistemleri", "emoji": "📊"},
                {"text": "Rota Planlaması", "emoji": "📝"}
            ],
            "OK AYARLARI": [
                {"text": "Ateşleme Kontrolü", "emoji": "🎯"},
                {"text": "Atış Hızı", "emoji": "⏱️"},
                {"text": "Doğruluk Kalibrasyonu", "emoji": "📏"}
            ]
        }
        return menu_buttons.get(menu_type, menu_buttons["AYARLAR"])
    
    def update_menu(self, menu_type):
        """Menü tipini günceller ve butonları yeniden oluşturur"""
        self.menu_type = menu_type
        self.title_label.setText(menu_type)
        if menu_type == "AYARLAR" and not hasattr(self, 'battery_label'):
            self.battery_info = self.get_battery_info()
            self.battery_label = QLabel(self.battery_info)
            self.battery_label.setStyleSheet("color: #555555; font-size: 16px; font-weight: bold; margin-left: 10px;")
            self.layout.insertWidget(1, self.battery_label)
            self.battery_timer = QTimer(self)
            self.battery_timer.timeout.connect(self.update_battery_info)
            self.battery_timer.start(60000)  # Her dakika güncelle
        self.create_menu_items()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 20, 20)
        painter.fillPath(path, QColor(240, 240, 240, 245))  # Daha opak beyaz  # Daha opak beyaz  # Daha opak beyaz

class BottomBar(QWidget):
    buttonClicked = Signal(int)  # Tıklanan butonun indisini gönderir
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        icons = [
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/settings.png",  # ⚙️
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/connection.png", # 🔌
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/controls.png",   # 🎛️
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/sound.png",      # 🔊
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/target.png",     # 🎯
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/camera.png",     # 📹
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/forward.png",    # ⏩
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/satellite.png",  # 📡
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/location.png",   # 📍
            "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/arrow.png"       # ➡️
        ]
        
        for i, icon_path in enumerate(icons):
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 30);
                    border-radius: 16px;
                }
            """)
            index = i
            btn.clicked.connect(lambda checked, idx=index: self.buttonClicked.emit(idx))
            layout.addWidget(btn)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 30, 30)
        painter.fillPath(path, QColor(200, 200, 200, 180))

class CloseButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        self.logo_label = QLabel()
        self.logo_path = "C:/Users/Oyun/Downloads/SAR/SAR FRONTEND/SAR GUI/icons/eclogo.png"
        self.logo_pixmap = QPixmap(self.logo_path).scaled(320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.confirm_dialog = None
    
    def mousePressEvent(self, event):
        self.show_confirm_dialog()
    
    def show_confirm_dialog(self):
        if self.confirm_dialog:
            return
        self.confirm_dialog = QWidget(self.window())
        self.confirm_dialog.setFixedSize(400, 200)
        parent_width = self.window().width()
        parent_height = self.window().height()
        dialog_x = (parent_width - self.confirm_dialog.width()) // 2
        dialog_y = (parent_height - self.confirm_dialog.height()) // 2
        self.confirm_dialog.move(dialog_x, dialog_y)
        layout = QVBoxLayout(self.confirm_dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        question = QLabel("S.A.R System'den ayrılıyorsunuz.")
        question.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        question.setAlignment(Qt.AlignCenter)
        layout.addWidget(question)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        yes_button = QPushButton("Evet")
        yes_button.setFixedSize(130, 50)
        yes_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color:  #333333;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        yes_button.setCursor(Qt.PointingHandCursor)
        yes_button.clicked.connect(QApplication.quit)
        buttons_layout.addWidget(yes_button)
        no_button = QPushButton("Hayır")
        no_button.setFixedSize(130, 50)
        no_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        no_button.setCursor(Qt.PointingHandCursor)
        no_button.clicked.connect(self.close_confirm_dialog)
        buttons_layout.addWidget(no_button)
        
        layout.addSpacing(20)
        layout.addLayout(buttons_layout)
        self.confirm_dialog.paintEvent = self.dialog_paint_event.__get__(self.confirm_dialog, QWidget)
        self.confirm_dialog.show()
    
    def close_confirm_dialog(self):
        if not self.confirm_dialog:
            return
        self.confirm_dialog.close()
        self.confirm_dialog.deleteLater()
        self.confirm_dialog = None
    
    def dialog_paint_event(self, event):
        painter = QPainter(self.confirm_dialog)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.confirm_dialog.rect(), 20, 20)
        painter.fillPath(path, QColor(60, 60, 60, 240))
        painter.setPen(QPen(QColor(80, 80, 80, 150), 2))
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
        self.thread = threading.Thread(target=self.collect_data)
        self.thread.daemon = True
        self.thread.start()
    
    def collect_data(self):
        while self.running:
            for sensor in self.data:
                if random.random() < 0.1:  # 10% chance to change status GUI made by E.R.D.3.M
                    if self.data[sensor]["status"] == "connected":
                        self.data[sensor]["status"] = "disconnected"
                        self.data[sensor]["signal"] = 0
                    else:
                        self.data[sensor]["status"] = "connected"
                        self.data[sensor]["signal"] = random.randint(1, 3)
            self.data_changed.emit(self.data.copy())
            time.sleep(2)
    
    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S.A.R System")
        self.setMinimumSize(1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.particle_bg = BackgroundEffects()
        self.main_layout.addWidget(self.particle_bg)
        self.weather_widget = WeatherWidget()
        self.weather_widget.setParent(self.central_widget)
        self.weather_widget.move(self.width() - self.weather_widget.width() - 10, 10)
        self.sar_text = QLabel("S.A.R SYSTEM")
        self.sar_text.setStyleSheet("color: #AAAAAA; font-size: 20px; font-weight: bold;")
        self.sar_text.setParent(self.central_widget)
        self.sar_text.setFixedSize(150, 30)
        self.content_container = QWidget(self.central_widget)
        self.content_container.setFixedSize(self.width(), self.height())
        self.side_menu = SideMenu()
        self.side_menu.setParent(self.central_widget)
        self.side_menu.move(-self.side_menu.width(), 0)  # Hidden initially
        self.side_menu.setFixedHeight(self.height())
        self.bottom_bar = BottomBar()
        self.bottom_bar.setParent(self.central_widget)
        self.bottom_bar.buttonClicked.connect(self.handle_button_click)
        self.close_button = CloseButton()
        self.close_button.setParent(self.central_widget)
        self.sensor_grid = QWidget(self.content_container)
        grid_layout = QGridLayout(self.sensor_grid)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        grid_layout.setSpacing(45)
        self.tiles = {
            "camera": WebcamWidget(),  # Kamera widget'ı
            "heat_sensor": ESP32CamTile("HEAT SENSOR", "http://<ESP32-CAM-IP>/capture"),  # ESP32-CAM URL'sini buraya yazın
            "ai_system": SensorTile("AI SYSTEM OUTPUT"),
            "sonar": SensorTile("SONAR SENSORS"),
            "surveillance": SensorTile("SURVEILLANCE CAM"),
            "tag_scanner": SensorTile("TAG SCANNER"),
        }
        grid_layout.addWidget(self.tiles["camera"], 0, 0)  # ESP32-CAM widget'ı sol üstte
        grid_layout.addWidget(self.tiles["heat_sensor"], 0, 1)
        grid_layout.addWidget(self.tiles["ai_system"], 0, 2)
        grid_layout.addWidget(self.tiles["sonar"], 1, 0)
        grid_layout.addWidget(self.tiles["surveillance"], 1, 1)
        grid_layout.addWidget(self.tiles["tag_scanner"], 1, 2)
        self.data_collector = SensorDataCollector()
        self.data_collector.data_changed.connect(self.update_sensor_data)
        self.menu_open = False
        self.menu_animation = None
        self.current_menu_button = None  # Track which button is currently active
        self.resizeEvent(None)
    
    def handle_button_click(self, button_index):
        button_titles = [
            "AYARLAR", "BAĞLANTILAR", "KONTROLLER", "SES AYARLARI", 
            "HEDEF AYARLARI", "KAMERA AYARLARI", "İLERİ AYARLAR", 
            "UYDU AYARLARI", "KONUM AYARLARI", "OK AYARLARI"
        ]
        
        if 0 <= button_index < len(button_titles):
            if self.current_menu_button == button_index and self.menu_open:
                self.hide_side_menu()
                self.current_menu_button = None
            else:
                menu_type = button_titles[button_index]
                self.side_menu.update_menu(menu_type)
                self.show_side_menu()
                self.current_menu_button = button_index
    
    def show_side_menu(self):
        if self.menu_animation and self.menu_animation.state() == QPropertyAnimation.Running:
            self.menu_animation.stop()
        menu_animation = QPropertyAnimation(self.side_menu, b"pos")
        menu_animation.setDuration(300)
        menu_animation.setStartValue(QPoint(-self.side_menu.width(), 0))
        menu_animation.setEndValue(QPoint(0, 0))  # Left-top corner (0,0)
        menu_animation.setEasingCurve(QEasingCurve.OutCubic)
        menu_animation.start()
        
        self.menu_open = True
        self.menu_animation = menu_animation

    def hide_side_menu(self):
        if self.menu_animation and self.menu_animation.state() == QPropertyAnimation.Running:
            self.menu_animation.stop()
        menu_animation = QPropertyAnimation(self.side_menu, b"pos")
        menu_animation.setDuration(300)
        menu_animation.setStartValue(QPoint(0, 0))
        menu_animation.setEndValue(QPoint(-self.side_menu.width(), 0))  # Slide to left
        menu_animation.setEasingCurve(QEasingCurve.OutCubic)
        menu_animation.start()
        
        self.menu_open = False
        self.menu_animation = menu_animation
    
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
                    tile.status_label.setStyleSheet("color: #88FF88; font-size: 24px;")
                else:
                    tile.status_label.setText("NO SIGNAL")
                    tile.status_label.setStyleSheet("color: #888888; font-size: 24px;")
    
    def resizeEvent(self, event):
        self.weather_widget.move(self.width() - self.weather_widget.width() - 20, 20)
        self.sar_text.move(
            self.width() - self.sar_text.width() - 10,
            self.height() - self.sar_text.height() - 10
        )
        self.side_menu.setFixedHeight(self.height())
        self.content_container.setFixedSize(self.width(), self.height())
        self.content_container.move(0, 0)  # Always at position 0,0
        grid_width = 3 * 450 + 2 * 45    # 3 columns * tile width + spacing
        grid_height = 2 * 315 + 45       # 2 rows * tile height + spacing
        self.sensor_grid.setFixedSize(grid_width, grid_height)
        self.sensor_grid.move(
            (self.width() - grid_width) // 2,
            (self.height() - grid_height) // 2
        )
        self.bottom_bar.setFixedWidth(min(700, self.width() - 40))
        self.bottom_bar.move(
            (self.width() - self.bottom_bar.width()) // 2,
            self.height() - self.bottom_bar.height() - 10
        )
        self.close_button.move(
            self.width() - 250,
            self.height() - 200
        )
    
    def closeEvent(self, event):
        self.data_collector.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()  # Use full screen for best effect
    sys.exit(app.exec())
