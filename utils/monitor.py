# utils/monitor.py - version corregida
import os
import time

from plyer import notification
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

TEMP_EXT = [".tmp", ".crdownload", ".part", ".download", ".partial", ".!bt", ".temp"]


class MonitorHandler(FileSystemEventHandler):
    def __init__(self, callback, folder_name):
        super().__init__()
        self.callback = callback
        self.folder_name = folder_name

    def on_created(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        ext = os.path.splitext(filename)[1].lower()
        # Notificar si el archivo creado ya es final
        if ext not in TEMP_EXT and not filename.startswith("."):
            self.callback("Descarga completada", f"Nuevo archivo: {filename}")

    def on_moved(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.dest_path)
        ext = os.path.splitext(filename)[1].lower()
        # Notificar cuando un archivo temporal se renombra a final
        if ext not in TEMP_EXT and not filename.startswith("."):
            self.callback("Descarga completada", f"Archivo finalizado: {filename}")


class FolderMonitorWorker(QObject):
    log_signal = pyqtSignal(str)

    def __init__(self, folders):
        super().__init__()
        self.folders = folders
        self.observers = []
        self.running = False

    def log(self, msg):
        self.log_signal.emit(msg)

    def run(self):
        self.running = True
        self.observers = []

        for folder in self.folders:
            if not os.path.exists(folder):
                self.log(f"No encontrada: {folder}")
                continue

            event_handler = MonitorHandler(
                lambda title, msg: self.notify(title, msg),
                os.path.basename(folder))
            observer = Observer()
            observer.schedule(event_handler, folder, recursive=False)
            observer.start()
            self.observers.append(observer)
            self.log(f"Monitoreando: {folder}")

        try:
            while self.running:
                time.sleep(0.5)
        except:
            pass

    def notify(self, title, message):
        # Intentar mostrar con el tray de Qt
        app = QApplication.instance()
        if app and hasattr(app, "window") and hasattr(app.window, "tray"):
            app.window.tray.showMessage(title, message)
        else:
            # Fallback con plyer
            notification.notify(
                title=title,
                message=message,
                app_name="Notificador",
                timeout=5
            )
        self.log(f"Notificacion: {message}")

    def stop(self):
        self.running = False
        for obs in self.observers:
            obs.stop()
            obs.join()
