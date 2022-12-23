#!/usr/bin/env python
# V 2022-12-02
#
# PDF's und JPEG-Bilder für das Internet DSGVO konform ohne Metadaten speichern.
# JPEG-Bilder auf eine maximale Pixelgröße verkleinern und komprimieren.
# Alle PDF's und JPEG-Bilder im gleichen Ordner und darunter (rekursiv) in welchem sich das Skript befindet,
# werden bearbeitet, siehe Settings.
#
# Benötigt folgende Python-Module: Pillow, pypdf2
#
# ACHTUNG! Die Dateien werden verändert, Backup sollte vorhanden sein!
#
from PIL import Image
import glob
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

# Settings:
max_size = 1280  # Maximal erlaubte Größe in Pixeln
compression = 80  # Qualität der JPEG-Komprimierung (0-100)
directory = os.getcwd()  # oder fest, z.B.: '/home/USER/MeineDateien'

def delete_pdf_metadata(path):
    # Dateiname und Pfad ohne Dateiname
    str_filename = path.split('/')[-1]
    str_path = path.replace(str_filename, '')
    pdf_writer = PdfFileWriter()
    # temporäre Datei erstellen, f-String = Stringformatierung
    tmp = f'{str_path}tmp.{str_filename}'
    # Öffnen der neuen Datei im Write-Modus und bestehende im Read-Modus
    with open(tmp, 'wb') as out:
        with open(path, 'rb') as pdf_in:
            # Seiten die noch Meta Daten enthalten suchen und eine Kopie mit neuen Meta Daten erstellen
            pdf = PdfFileReader(pdf_in)
            for page in range(pdf.getNumPages()):
                pdf_writer.addPage(pdf.getPage(page))
            # Metadaten schreiben
            pdf_writer.addMetadata(metadata)
            pdf_writer.write(out)
    os.remove(path)
    os.rename(tmp, str_path + str_filename)

def delete_jpg_metadata(path):
    # Entfernen der Metadaten und max. Größe mit Pillow
    image = Image.open(path)
    width, height = image.size

    # Größe des Bildes ändern, wenn es größer als max_size ist
    if width > max_size or height > max_size:
        size = (max_size, max_size)
        image.thumbnail(size, Image.Resampling.LANCZOS)
    image.save(path, "JPEG", exif=b"", quality=compression, optimize=True)

if __name__ == "__main__":

    # PDF Metadaten
    metadata = {
        '/Title': '',
        '/Subject': '',
        '/Author': '',
        '/Creator': '',
        '/Producer': '',
        '/CreationDate': '',
        '/MotDate': ''
    }

    # Umbenennen der Dateierweiterungen aller Dateien im Verzeichnis in Kleinbuchstaben
    # Liste aller Dateien im Verzeichnis (rekursiv)
    files = glob.iglob(f'{directory}/**/*.*', recursive=True)
    # Durchlaufen der Liste mit den Dateien
    for file in files:
        # Abfrage der Dateierweiterung
        file_ext = os.path.splitext(file)[1]
        # Dateierweiterung in Kleinbuchstaben umwandeln
        file_ext_lower = file_ext.lower()
        # Abrufen des Dateinamens ohne Erweiterung
        file_name = os.path.splitext(file)[0]
        # Benennen der Datei mit Kleinbuchstaben Erweiterung
        os.rename(file, file_name + file_ext_lower)

    # Alle PDF's im Ordner und Unterverzeichnisse (rekursiv)
    for path in glob.iglob(f'{directory}/**/*.pdf', recursive=True):
        delete_pdf_metadata(path)
        print(path)

    # Alle JPEG's im Ordner und Unterverzeichnisse (rekursiv)
    # funktioniert nicht :-\
    # for path in glob.iglob(f'{directory}/**/*.{jpg,jpeg}', recursive=True):
    # darum 2x
    for path in glob.iglob(f'{directory}/**/*.jpg', recursive=True):
        delete_jpg_metadata(path)
        print(path)
    for path in glob.iglob(f'{directory}/**/*.jpeg', recursive=True):
        delete_jpg_metadata(path)
        print(path)
