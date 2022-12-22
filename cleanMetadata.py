#!/usr/bin/env python
# V 2022-12-01
#
# PDF und JPEG-Bilder für das Internet DSGVO konform ohne Metadaten speichern
# JPEG Bilder auf eine maximale Pixelgröße verkleinern und komprimieren
# Alle PDF's und JPEG-Bilder im gleichen Ordner und darunter (rekursiv) wie das Skript werden bearbeitet, siehe Settings
#
# Benötigt folgende Python-Module: Pillow, pypdf2
#
# ACHTUNG! Die Dateien werden verändert! Backup sollte vorhanden sein!
#
from PIL import Image
import glob
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

# Settings:
max_size = 1280  # Maximal erlaubte Größe in Pixeln
compression = 80  # Qualität der JPEG-Komprimierung (0-100)
directory = os.getcwd()  # oder fest, z.B.: '/home/USER/MeineDateien'

def delete_pdf_metadata(full_path):
    # Dateiname und Pfad ohne Dateiname
    str_filename = full_path.split('/')[-1]
    str_path = full_path.replace(str_filename, '')
    pdf_writer = PdfFileWriter()
    # temporäre Datei erstellen, f-String = Stringformatierung
    tmp = f'{str_path}tmp.{str_filename}'
    # Öffnen der neuen Datei im Write-Modus und bestehende im Read-Modus
    with open(tmp, 'wb') as out:
        with open(full_path, 'rb') as pdf_in:
            # Seiten die noch Meta Daten enthalten suchen und eine Kopie mit neuen Meta Daten erstellen
            pdf = PdfFileReader(pdf_in)
            for page in range(pdf.getNumPages()):
                pdf_writer.addPage(pdf.getPage(page))
            # Metadaten schreiben
            pdf_writer.addMetadata(metadata)
            pdf_writer.write(out)
    os.remove(full_path)
    os.rename(tmp, str_path + str_filename)

def delete_jpg_metadata(full_path):
    # Bilder öffnen mit Pillow
    for file in os.listdir(directory):
        extension = file.lower()[-4:]
        if extension == ".jpg" or extension == ".jpeg":
            image = Image.open(os.path.join(directory, file))
            width, height = image.size

            if width > max_size or height > max_size:
                ratio = min(max_size / width, max_size / height)
                image = image.resize((int(width * ratio), int(height * ratio)))

            # Entfernen der Metadaten
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)
            # Bild ohne Metadaten speichern
            image_without_exif.save(os.path.join(directory, file), quality=compression)


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
    # funktioniert nicht, darum 2x :-\
    # for path in glob.iglob(f'{directory}/**/*.{jpg,jpeg}', recursive=True):
    for path in glob.iglob(f'{directory}/**/*.jpg', recursive=True):
        delete_jpg_metadata(path)
        print(path)
    for path in glob.iglob(f'{directory}/**/*.jpeg', recursive=True):
        delete_jpg_metadata(path)
        print(path)
