# Homeworks
Eğer alt menüler gelmezse , kaynak kodundan /icons klasörünün mutlak dosya yolunu elle tek tek girin.Sonra mevcut qrc dosyalarını silin ve baştan tanılama yapın.

resources.qrc dosyasını projenizdeki ana dizine koy(hem icons içine hem SAR GUI YE BAŞTAN QRC TANIMLAMA). Dosya içeriği : 

<!DOCTYPE RCC>
<RCC>
    <qresource prefix="/icons">
        <file>icons/sunny.png</file>
        <file>icons/partly_cloudy.png</file>
        <file>icons/cloudy.png</file>
        <file>icons/rainy.png</file>
        <file>icons/snowy.png</file>
        <file>icons/stormy.png</file>
    </qresource>
</RCC>


Vscode da terminal açıp , 

cd dosya yolu\SAR GUI
pyside6-rcc resources.qrc -o resources_rc.py
yazın.

Sonra kodu çalıştırın.
