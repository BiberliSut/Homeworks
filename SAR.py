
import sys
import subprocess
import importlib.util
import threading
import tkinter as tk

root = tk.Tk()
root.title("Yükleniyor...")
root.geometry("300x100")
root.resizable(False, False)
label = tk.Label(root, text="Ön gereksinimler denetleniyor...\nLütfen bekleyin.", font=("Arial", 10))
label.pack(expand=True)

def check_and_continue():
    required = ['PySide6', 'requests']
    for pkg in required:
        if importlib.util.find_spec(pkg) is None:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
    root.destroy()

threading.Thread(target=check_and_continue, daemon=True).start()
root.mainloop()

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
                          QPainterPath, QPixmap, QIcon)
from PySide6.QtGui import QTransform

class BackgroundEffects(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Ekran boyutlarını al
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        
        # Irili ufaklı parçacıklar için ayarlar - opaklık değerlerini arttırdım
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

        # Sol üstten gelen ışık huzmesi için ayarlar
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
        
        # İkincil ışık huzmeleri (daha küçük ve farklı açılarda)
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
        
        # Bulanıklık efekti ekle
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(8)  # Bulanıklık miktarını artırdım
        self.setGraphicsEffect(self.blur_effect)
    
    def resizeEvent(self, event):
        # Widget yeniden boyutlandırıldığında ekran boyutlarını güncelle
        super().resizeEvent(event)
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        
        # Parçacıkları yeniden dağıt
        for p in self.particles:
            p['x'] = random.randint(0, self.screen_width)
            p['y'] = random.randint(0, self.screen_height)

        # Ana ışık huzmesi boyutlarını güncelle
        self.main_light_beam['length'] = self.screen_width * 1.5
        self.main_light_beam['width_end'] = self.screen_width
        
        # İkincil ışık huzmelerini güncelle
        for beam in self.secondary_beams:
            beam['length'] = self.screen_width * random.uniform(0.8, 1.2)

    def update_effects(self):
        # Ekran boyutlarını güncelle
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        
        # Parçacıkları güncelle
        for p in self.particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            
            # Ekranın dışına çıkan parçacıkları ekranın diğer tarafından tekrar gir  GUI made by E.R.D.E.M  E.R.Ç.E.T.İ.N
            if p['x'] < -p['size']:
                p['x'] = self.screen_width + p['size']
            elif p['x'] > self.screen_width + p['size']:
                p['x'] = -p['size']
                
            if p['y'] < -p['size']:
                p['y'] = self.screen_height + p['size']
            elif p['y'] > self.screen_height + p['size']:
                p['y'] = -p['size']
        
        # Ana ışık huzmesi animasyonu
        self.main_light_beam['phase'] += self.main_light_beam['speed']
        pulse_factor = 0.15 * math.sin(self.main_light_beam['phase']) + 0.85  # Işık yanıp sönmesi
        self.main_light_beam['opacity'] = 0.12 * pulse_factor
        
        # İkincil ışık huzmeleri animasyonu
        for beam in self.secondary_beams:
            beam['phase'] += beam['speed']
            beam_pulse = 0.2 * math.sin(beam['phase']) + 0.8
            beam['opacity'] = (0.05 + 0.02 * beam_pulse) * pulse_factor
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Geçerli ekran boyutlarını al
        screen_width = self.screen_width
        screen_height = self.screen_height
        
        # Koyu gradyan arka planı çiz
        gradient = QLinearGradient(0, 0, 0, screen_height)
        gradient.setColorAt(0, QColor(20, 20, 40))
        gradient.setColorAt(1, QColor(10, 10, 20))
        painter.fillRect(self.rect(), gradient)
        
        # ÖNEMLİ DEĞİŞİKLİK: Çizim sırasını değiştirdim
        # Önce ışık huzmelerini çiz
        
        # 1. Ana ışık huzmesini çiz (sol üstten gelen sönük ışık)
        painter.save()
        
        # Ana ışık huzmesi için dönüşüm
        transform = QTransform()
        transform.translate(self.main_light_beam['origin_x'], self.main_light_beam['origin_y'])
        transform.rotate(self.main_light_beam['angle'])
        painter.setTransform(transform)
        
        # Ana ışık huzmesi için gradyan
        beam_gradient = QLinearGradient(0, 0, self.main_light_beam['length'], 0)
        start_color = self.main_light_beam['color_start']
        start_color.setAlpha(int(255 * self.main_light_beam['opacity']))
        end_color = self.main_light_beam['color_end']
        end_color.setAlpha(int(10 * self.main_light_beam['opacity']))
        
        beam_gradient.setColorAt(0, start_color)
        beam_gradient.setColorAt(1, end_color)
        
        # Genişleyen ışık huzmesi için yol oluştur (üçgen şeklinde)
        beam_path = QPainterPath()
        beam_path.moveTo(0, 0)
        beam_path.lineTo(self.main_light_beam['length'], -self.main_light_beam['width_end'] / 2)
        beam_path.lineTo(self.main_light_beam['length'], self.main_light_beam['width_end'] / 2)
        beam_path.closeSubpath()
        
        painter.fillPath(beam_path, beam_gradient)
        painter.restore()
        
        # 2. İkincil ışık huzmelerini çiz
        for beam in self.secondary_beams:
            painter.save()
            
            # İkincil ışık huzmesi için dönüşüm
            transform = QTransform()
            transform.translate(beam['origin_x'], beam['origin_y'])
            transform.rotate(beam['angle'])
            painter.setTransform(transform)
            
            # İkincil ışık huzmesi için gradyan
            sec_beam_gradient = QLinearGradient(0, 0, beam['length'], 0)
            sec_start_color = beam['color_start']
            sec_start_color.setAlpha(int(255 * beam['opacity']))
            sec_end_color = beam['color_end']
            sec_end_color.setAlpha(int(5 * beam['opacity']))
            
            sec_beam_gradient.setColorAt(0, sec_start_color)
            sec_beam_gradient.setColorAt(1, sec_end_color)
            
            # İkincil ışık huzmesi için yol
            sec_beam_path = QPainterPath()
            sec_beam_path.moveTo(0, 0)
            sec_beam_path.lineTo(beam['length'], -beam['width_end'] / 2)
            sec_beam_path.lineTo(beam['length'], beam['width_end'] / 2)
            sec_beam_path.closeSubpath()
            
            painter.fillPath(sec_beam_path, sec_beam_gradient)
            painter.restore()
        
        # 3. Ten renkli parçacıkları çiz - SONRA ÇİZEREK IŞIĞIN ÜSTÜNDE GÖRÜNMESINI SAĞLIYORUZ
        # BlendMode.SourceOver ekleyerek karıştırma modunu değiştiriyoruz
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        for p in self.particles:
            # Parçacık boyutu ve opaklık ayarlarını değiştirdim
            # Büyük parçacıkların daha belirgin olmasını sağlıyorum
            size_factor = p['size'] / 25.0
            # Büyük parçacıklar daha opak, küçükler daha şeffaf
            opacity_factor = 0.3 + (size_factor * 0.7)  # Değerleri 0.3-1.0 arasında tutar
            
            # Parçacık renklerini daha parlak yapma
            particle_color = p['color']
            # Opaklığı artırarak daha belirgin hale getiriyoruz
            particle_color.setAlpha(int(255 * opacity_factor * p['opacity']))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(particle_color)
            
            # Parçacığı konumuna çiz - boyutu biraz büyüttüm
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
        # Sensör kutularını 4 kat büyüt (200x140 -> 800x560)
        self.setFixedSize(450, 315)  # Ekranda düzgün görünmesi için boyutu ayarlandı
        self.title = title
        self.has_signal = False
        self.signal_strength = 0
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)  # Margin'leri ayarladık
        layout.setAlignment(Qt.AlignCenter)
        
        # Signal strength indicator
        self.signal_indicator = SignalStrengthIndicator()
        # Sinyal göstergesini de büyütelim
        self.signal_indicator.setFixedSize(40, 40)  # Orijinal boyutunu koruduk Code Author Erdem Erçetin
        layout.addWidget(self.signal_indicator, 0, Qt.AlignCenter)
        
        # Title label - yazı boyutunu büyüttük
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #AAAAAA; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Status label - yazı boyutunu büyüttük
        self.status_label = QLabel("NO SIGNAL")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-size: 21px;")
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
            self.status_label.setStyleSheet("color: #88FF88; font-size: 21px;")
        else:
            self.signal_strength = max(0, self.signal_strength - 1)
            self.status_label.setText("NO SIGNAL")
            self.status_label.setStyleSheet("color: #888888; font-size: 21px;")
            
        self.signal_indicator.set_signal_level(self.signal_strength)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 30, 30)
        painter.fillPath(path, QColor(0, 0, 0, 220))
        
        # Draw subtle border
        painter.setPen(QPen(QColor(50, 50, 50, 100), 1))
        painter.drawPath(path)



class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 70)
        
        # İkon dizinlerini belirle
        self.icons_dir = Path(__file__).parent / "icons"
        
        # Hava durumu koşullarını ikon dosya isimlerine eşleştir
        self.weather_icons = {
            "Sunny": "SAR GUI/icons/sunny.png",
            "Clear": "SAR GUI/icons/sunny.png",
            "Partly cloudy": "SAR GUI/icons/partly_cloudy.png",
            "Cloudy": "SAR GUI/icons/cloudy.png",
            "Overcast": "SAR GUI/icons/cloudy.png",
            "Mist": "SAR GUI/icons/cloudy.png",
            "Patchy rain possible": "SAR GUI/icons/rainy.png",
            "Light rain": "SAR GUI/icons/rainy.png",
            "Moderate rain": "SAR GUI/icons/rainy.png",
            "Heavy rain": "SAR GUI/icons/rainy.png",
            "Light snow": "SAR GUI/icons/snowy.png",
            "Moderate snow": "SAR GUI/icons/snowy.png",
            "Heavy snow": "SAR GUI/icons/snowy.png",
            "Thunderstorm": "SAR GUI/icons/stormy.png",
            "Thunder": "SAR GUI/icons/stormy.png"
        }
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        # Layout boşluklarını sıfırla - ikonu sola kaydırmak için
        layout.setSpacing(0)
        
        # Zaman ve tarih
        time_date_layout = QVBoxLayout()
        
        self.time_label = QLabel("15:50")
        self.time_label.setStyleSheet("color: #333333; font-size: 20px; font-weight: bold;")
        time_date_layout.addWidget(self.time_label)
        
        self.date_label = QLabel("10/04/2025")
        self.date_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        time_date_layout.addWidget(self.date_label)
        
        layout.addLayout(time_date_layout)
        
        # Hava durumu ikonu - boyutu büyütüldü ve sol margin eklendi
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(70, 70)
        # Sol margin ekleyerek ikonu sola kaydırıyoruz
        self.weather_icon.setContentsMargins(0, -10, 0, 0)
        layout.addWidget(self.weather_icon)
        
        # Sıcaklık ve gün - sağ margin ile sağdaki yazıları da uygun şekilde ayarlıyoruz
        temp_day_layout = QVBoxLayout()
        temp_day_layout.setContentsMargins(10, 0, 0, 0)  # Sol tarafa boşluk ekleyerek ikona yaklaştırıyoruz
        
        self.temp_label = QLabel("25°C")
        self.temp_label.setStyleSheet("color: #333333; font-size: 20px; font-weight: bold;")
        temp_day_layout.addWidget(self.temp_label)
        
        self.day_label = QLabel("PERŞEMBE")
        self.day_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        temp_day_layout.addWidget(self.day_label)
        
        layout.addLayout(temp_day_layout)
        
        # Layout ağırlıklarını ayarlayarak bileşenlerin konumlarını düzenliyoruz
        layout.setStretch(0, 2)  # Zaman-tarih kısmına daha az yer
        layout.setStretch(1, 3)  # İkona daha fazla yer
        layout.setStretch(2, 2)  # Sıcaklık-gün kısmına daha az yer
        
        # Varsayılan ikon yükle
        self.set_default_icon()
        
        # Güncelleme timer'ı
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(300000)  # Her 5 dakikada bir güncelle
        
        # İlk verileri ayarla
        self.update_weather()
    
    def set_default_icon(self):
        """Varsayılan ikonu yükle"""
        try:
            # Önce resource'dan yüklemeyi dene
            icon_path = "SAR GUI/icons/partly_cloudy.png"
            pixmap = QPixmap(icon_path)
            
            # Eğer başarısız olursa, dosya sisteminden dene
            if pixmap.isNull():
                icon_path = str(self.icons_dir / "partly_cloudy.png")
                pixmap = QPixmap(icon_path)
                
            if not pixmap.isNull():
                # İkon boyutu 70x70 olarak ayarlandı
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
        # Önce resource'dan yüklemeyi dene
        for key in self.weather_icons:
            if key.lower() in condition.lower():
                return f":/icons/icons/{self.weather_icons[key]}"
        
        # Eğer eşleşme bulunamazsa, varsayılan ikonu döndür
        return "SAR GUI/icons/partly_cloudy.png"
    
    def update_weather(self):
        # Zaman ve tarihi API durumundan bağımsız olarak güncelle
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%d/%m/%Y"))
        
        # Türkçe gün isimlerini belirle -  Code Author Erdem Erçetin
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
        
        # API'dan hava durumu verisini almaya çalış
        weather_data = self.get_weather_data()
        
        if weather_data:
            try:
                # Sıcaklık ve hava durumu bilgisini çıkar
                temp = weather_data["current_condition"][0]["temp_C"]
                condition = weather_data["current_condition"][0]["weatherDesc"][0]["value"]
                
                # Sıcaklık etiketini güncelle
                self.temp_label.setText(f"{temp}°C")
                
                # Hava durumu ikonu güncelle
                try:
                    icon_path = self.get_icon_path(condition)
                    pixmap = QPixmap(icon_path)
                    
                    if pixmap.isNull():
                        # Resource başarısız olursa, dosya sisteminden yüklemeyi dene
                        for key in self.weather_icons:
                            if key.lower() in condition.lower():
                                file_path = str(self.icons_dir / self.weather_icons[key])
                                pixmap = QPixmap(file_path)
                                if not pixmap.isNull():
                                    break
                    
                    if not pixmap.isNull():
                        # İkon boyutu 60x60 olarak ayarlandı
                        self.weather_icon.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    else:
                        # Varsayılan ikonu yükle
                        self.set_default_icon()
                        
                except Exception as e:
                    print(f"İkon yükleme hatası: {e}")
                    self.set_default_icon()
                    
            except Exception as e:
                print(f"Hava durumu veri işleme hatası: {e}")
                self.set_default_icon()
        else:
            # API çağrısı başarısız olursa, varsayılan ikonu kullan
            self.set_default_icon()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Yuvarlatılmış dikdörtgen arka plan - beyaz dinamik ada
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 35, 35)
        
        # Hafif şeffaflıkla beyaz arka plan
        painter.fillPath(path, QColor(240, 240, 240, 240))
        
        # İnce bir kenarlık ekle
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        painter.drawPath(path) # Slightly darker and less transparent # Slightly darker and less transparent

class SideMenu(QWidget):
    def __init__(self, menu_type="AYARLAR", parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)  # Menüyü daha geniş yapma
        self.menu_type = menu_type
        
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 50, 20, 20)
        self.layout.setSpacing(25)
        
        # Title
        self.title_label = QLabel(menu_type)
        self.title_label.setStyleSheet("color: #333333; font-size: 22px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Pil durumu veya güç kaynağı bilgisi (sadece AYARLAR menüsünde gösterilecek)
        if menu_type == "AYARLAR":
            self.battery_info = self.get_battery_info()
            self.battery_label = QLabel(self.battery_info)
            self.battery_label.setStyleSheet("color: #555555; font-size: 16px; font-weight: bold; margin-left: 10px;")
            self.layout.addWidget(self.battery_label)
            
            # Pil bilgisini periyodik olarak güncelleyen timer
            self.battery_timer = QTimer(self)
            self.battery_timer.timeout.connect(self.update_battery_info)
            self.battery_timer.start(60000)  # Her dakika güncelle
        
        # Menü öğelerini doldur
        self.create_menu_items()
        
        # Layout'a boşluk ekle
        self.layout.addStretch()
    
    def get_battery_info(self):
        """Sistem pil bilgisini alır"""
        try:
            # psutil kütüphanesi yüklü değilse bunu ele al
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
            # psutil yoksa veya pil bilgisi alınamazsa
            import sys
            if sys.platform == 'win32':
                # Windows için basit bir kontrol yapalım
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
        # Önce mevcut butonları temizle (başlık ve pil bilgisi hariç)
        for i in reversed(range(2 if self.menu_type == "AYARLAR" else 1, self.layout.count())):
            item = self.layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        # Menü tipine göre butonlar ekle
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
        
        # Seçilen menü tipi için butonları döndür, yoksa varsayılan olarak AYARLAR menüsünü göster
        return menu_buttons.get(menu_type, menu_buttons["AYARLAR"])
    
    def update_menu(self, menu_type):
        """Menü tipini günceller ve butonları yeniden oluşturur"""
        self.menu_type = menu_type
        self.title_label.setText(menu_type)
        
        # Eğer AYARLAR menüsü ise ve battery_label yoksa, oluştur
        if menu_type == "AYARLAR" and not hasattr(self, 'battery_label'):
            self.battery_info = self.get_battery_info()
            self.battery_label = QLabel(self.battery_info)
            self.battery_label.setStyleSheet("color: #555555; font-size: 16px; font-weight: bold; margin-left: 10px;")
            self.layout.insertWidget(1, self.battery_label)
            
            # Pil bilgisini periyodik olarak güncelleyen timer
            self.battery_timer = QTimer(self)
            self.battery_timer.timeout.connect(self.update_battery_info)
            self.battery_timer.start(60000)  # Her dakika güncelle
        
        # Menüyü yeniden oluştur
        self.create_menu_items()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 20, 20)
        painter.fillPath(path, QColor(240, 240, 240, 245))  # Daha opak beyaz  # Daha opak beyaz  # Daha opak beyaz

class BottomBar(QWidget):
    buttonClicked = Signal(int)  # Tıklanan butonun indisini gönderir
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Icon dosya yolları
        icons = [
            "SAR GUI/icons/settings.png",  # ⚙️
            "SAR GUI/icons/connection.png", # 🔌
            "SAR GUI/icons/controls.png",   # 🎛️
            "SAR GUI/icons/sound.png",      # 🔊
            "SAR GUI/icons/target.png",     # 🎯
            "SAR GUI/icons/camera.png",     # 📹
            "SAR GUI/icons/forward.png",    # ⏩
            "SAR GUI/icons/satellite.png",  # 📡
            "SAR GUI/icons/location.png",   # 📍
            "SAR GUI/icons/arrow.png"       # ➡️
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
            # İndis numarasını button'a bağlayarak hangi butonun tıklandığını bilelim
            index = i
            btn.clicked.connect(lambda checked, idx=index: self.buttonClicked.emit(idx))
            layout.addWidget(btn)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 30, 30)
        painter.fillPath(path, QColor(200, 200, 200, 180))

# SARBadge sınıfını şununla değiştirebilirsiniz:

class CloseButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        
        # Sadece ikon içeren düzen
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        
        # İkonu doğrudan bu widget'a yerleştir
        self.logo_label = QLabel()
        self.logo_path = "SAR GUI/icons/eclogo.png"
        self.logo_pixmap = QPixmap(self.logo_path).scaled(320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)
        
        # Tüm widget'ı tıklanabilir yap
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Onay iletişim kutusu
        self.confirm_dialog = None
    
    # Removed enterEvent, leaveEvent, mouseReleaseEvent animations
    
    def mousePressEvent(self, event):
        # Show confirmation dialog without animations
        self.show_confirm_dialog()
    
    def show_confirm_dialog(self):
        # Eğer dialog zaten açıksa, yenisini açma
        if self.confirm_dialog:
            return
            
        # Yeni bir dialog widget'ı oluştur
        self.confirm_dialog = QWidget(self.window())
        self.confirm_dialog.setFixedSize(400, 200)
        
        # Dialog'u ekranın ortasına konumlandır
        parent_width = self.window().width()
        parent_height = self.window().height()
        dialog_x = (parent_width - self.confirm_dialog.width()) // 2
        dialog_y = (parent_height - self.confirm_dialog.height()) // 2
        self.confirm_dialog.move(dialog_x, dialog_y)
        
        # Layout
        layout = QVBoxLayout(self.confirm_dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Soru
        question = QLabel("S.A.R System'den ayrılıyorsunuz.")
        question.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        question.setAlignment(Qt.AlignCenter)
        layout.addWidget(question)
        
        # Butonlar için layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        
        # Evet butonu
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
        
        # Hayır butonu
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
        
        # Dialog arka planı
        self.confirm_dialog.paintEvent = self.dialog_paint_event.__get__(self.confirm_dialog, QWidget)
        
        # Dialog'u göster (animation olmadan)
        self.confirm_dialog.show()
    
    def close_confirm_dialog(self):
        if not self.confirm_dialog:
            return
        
        # Animasyon olmadan kapat
        self.confirm_dialog.close()
        self.confirm_dialog.deleteLater()
        self.confirm_dialog = None
    
    def dialog_paint_event(self, event):
        painter = QPainter(self.confirm_dialog)
        painter.setRenderHint(QPainter.Antialiasing)
    
    # Yuvarlatılmış dikdörtgen arka plan - koyu gri olarak güncellendi
        path = QPainterPath()
        path.addRoundedRect(self.confirm_dialog.rect(), 20, 20)
    
    # Koyu gri arka plan
        painter.fillPath(path, QColor(60, 60, 60, 240))
    
    # İnce kenarlık
        painter.setPen(QPen(QColor(80, 80, 80, 150), 2))
        painter.drawPath(path)
    
    # No paintEvent needed since we're not drawing the hexagon
    
    # Remove the paintEvent method that draws the hexagon shape
    
 

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
                if random.random() < 0.1:  # 10% chance to change status GUI made by E.R.D.3.M
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
        self.setMinimumSize(1200, 800)
        
        # Central widget with transparent background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Background effects widget
        self.particle_bg = BackgroundEffects()
        self.main_layout.addWidget(self.particle_bg)
        
        # Weather widget (top right)
        self.weather_widget = WeatherWidget()
        self.weather_widget.setParent(self.central_widget)
        self.weather_widget.move(self.width() - self.weather_widget.width() - 10, 10)
        
        # SAR SYSTEM yazısı (sağ alt köşe)
        self.sar_text = QLabel("S.A.R SYSTEM")
        self.sar_text.setStyleSheet("color: #AAAAAA; font-size: 20px; font-weight: bold;")
        self.sar_text.setParent(self.central_widget)
        self.sar_text.setFixedSize(150, 30)
        
        # Create a container for all the center content
        self.content_container = QWidget(self.central_widget)
        self.content_container.setFixedSize(self.width(), self.height())
        
        # Side menu (initially hidden)
        self.side_menu = SideMenu()
        self.side_menu.setParent(self.central_widget)
        self.side_menu.move(-self.side_menu.width(), 0)  # Hidden initially
        self.side_menu.setFixedHeight(self.height())
        
        # Bottom bar
        self.bottom_bar = BottomBar()
        self.bottom_bar.setParent(self.central_widget)
        self.bottom_bar.buttonClicked.connect(self.handle_button_click)
        
        # S.A.R badge with eclogo
        self.close_button = CloseButton()
        self.close_button.setParent(self.central_widget)
        
        # Create sensor grid container
        self.sensor_grid = QWidget(self.content_container)
        grid_layout = QGridLayout(self.sensor_grid)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        grid_layout.setSpacing(45)
        
        # Create sensor tiles
        self.tiles = {
            "camera": SensorTile("CAMERA"),
            "heat_sensor": SensorTile("HEAT SENSOR"),
            "ai_system": SensorTile("AI SYSTEM OUTPUT"),
            "sonar": SensorTile("SONAR SENSORS"),
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
        
        # Sensor data collector
        self.data_collector = SensorDataCollector()
        self.data_collector.data_changed.connect(self.update_sensor_data)
        
        # Menu state tracking
        self.menu_open = False
        self.menu_animation = None
        self.current_menu_button = None  # Track which button is currently active
        
        # Resize event to position widgets correctly
        self.resizeEvent(None)
    
    def handle_button_click(self, button_index):
        # Define button titles as shown in your image
        button_titles = [
            "AYARLAR", "BAĞLANTILAR", "KONTROLLER", "SES AYARLARI", 
            "HEDEF AYARLARI", "KAMERA AYARLARI", "İLERİ AYARLAR", 
            "UYDU AYARLARI", "KONUM AYARLARI", "OK AYARLARI"
        ]
        
        if 0 <= button_index < len(button_titles):
            # Check if the same button was clicked
            if self.current_menu_button == button_index and self.menu_open:
                # If clicking the same button and menu is open, close it
                self.hide_side_menu()
                self.current_menu_button = None
            else:
                # Different button or menu closed, update menu type and show menu
                menu_type = button_titles[button_index]
                self.side_menu.update_menu(menu_type)
                self.show_side_menu()
                self.current_menu_button = button_index
    
    def show_side_menu(self):
        # Stop any existing animation
        if self.menu_animation and self.menu_animation.state() == QPropertyAnimation.Running:
            self.menu_animation.stop()
        
        # Menu animation - ÜSTTEN AÇILACAK ŞEKİLDE GÜNCELLEME   Programmed by BiberliSut
        menu_animation = QPropertyAnimation(self.side_menu, b"pos")
        menu_animation.setDuration(300)
        menu_animation.setStartValue(QPoint(-self.side_menu.width(), 0))
        menu_animation.setEndValue(QPoint(0, 0))  # Left-top corner (0,0)
        menu_animation.setEasingCurve(QEasingCurve.OutCubic)
        menu_animation.start()
        
        self.menu_open = True
        
        # Save reference to animation to avoid garbage collection
        self.menu_animation = menu_animation

    def hide_side_menu(self):
        # Stop any existing animation
        if self.menu_animation and self.menu_animation.state() == QPropertyAnimation.Running:
            self.menu_animation.stop()
        
        # Menu animation to hide - ÜSTTEN SAKLANACAK ŞEKİLDE GÜNCELLEME
        menu_animation = QPropertyAnimation(self.side_menu, b"pos")
        menu_animation.setDuration(300)
        menu_animation.setStartValue(QPoint(0, 0))
        menu_animation.setEndValue(QPoint(-self.side_menu.width(), 0))  # Slide to left
        menu_animation.setEasingCurve(QEasingCurve.OutCubic)
        menu_animation.start()
        
        self.menu_open = False
        
        # Save reference to animation to avoid garbage collection
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
        # Position weather widget
        self.weather_widget.move(self.width() - self.weather_widget.width() - 20, 20)
        
        # Position SAR SYSTEM text in bottom right
        self.sar_text.move(
            self.width() - self.sar_text.width() - 10,
            self.height() - self.sar_text.height() - 10
        )
        
        # Size for the side menu
        self.side_menu.setFixedHeight(self.height())
        
        # Position content container to take whole screen
        self.content_container.setFixedSize(self.width(), self.height())
        self.content_container.move(0, 0)  # Always at position 0,0
        
        # Position sensor grid within content container
        grid_width = 3 * 450 + 2 * 45    # 3 columns * tile width + spacing
        grid_height = 2 * 315 + 45       # 2 rows * tile height + spacing
        self.sensor_grid.setFixedSize(grid_width, grid_height)
        self.sensor_grid.move(
            (self.width() - grid_width) // 2,
            (self.height() - grid_height) // 2
        )
        
        # Position bottom bar
        self.bottom_bar.setFixedWidth(min(700, self.width() - 40))
        self.bottom_bar.move(
            (self.width() - self.bottom_bar.width()) // 2,
            self.height() - self.bottom_bar.height() - 10
        )
        
        # Position close button at the bottom right
        self.close_button.move(
            self.width() - 250,
            self.height() - 200
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
