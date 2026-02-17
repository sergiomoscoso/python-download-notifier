# main.py - Notificador de Descargas (version corregida)
import json
import os
import sys

from PyQt6.QtCore import QThread
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

CONFIG_FILE = "config.json"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notificador de Descargas")
        self.resize(400, 300)

        # 1. Crear el widget de log
        self.log = QListWidget()

        # 2. Cargar la configuracion
        self.config = self.load_config()

        # 3. Crear los demas widgets
        self.label = QLabel("Carpetas monitoreadas:")
        self.list_folders = QListWidget()
        self.btn_add = QPushButton("Añadir carpeta")
        self.btn_remove = QPushButton("Eliminar")
        self.btn_start = QPushButton("Iniciar monitoreo")
        self.btn_stop = QPushButton("Detener")
        self.btn_stop.setEnabled(False)

        # Grupo de carpetas
        group_folders = QGroupBox()
        layout_folders = QVBoxLayout()
        layout_folders.addWidget(self.list_folders)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        layout_folders.addLayout(btn_layout)
        group_folders.setLayout(layout_folders)

        # Diseño principal
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(group_folders)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(QLabel("Eventos:"))
        layout.addWidget(self.log)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Añadir carpetas desde config
        self.list_folders.addItems(self.config.get("folders", []))

        # Variables internas
        self.monitor_thread = None
        self.monitor_worker = None

        # Conexiones de botones
        self.btn_add.clicked.connect(self.add_folder)
        self.btn_remove.clicked.connect(self.remove_folder)
        self.btn_start.clicked.connect(self.start_monitoring)
        self.btn_stop.clicked.connect(self.stop_monitoring)

        # Bandeja del sistema
        self.create_tray_icon()

        # Guardar referencia global en QApplication
        app = QApplication.instance()
        if app:
            app.window = self

        # Mensaje inicial
        self.add_log("App iniciada. Añade una carpeta y haz clic en 'Iniciar monitoreo'.")

    def create_tray_icon(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon.fromTheme("folder"))
        menu = QMenu()
        show_action = QAction("Mostrar", self)
        quit_action = QAction("Salir", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_click)
        self.tray.show()

    def on_tray_click(self, reason):
        if reason == 3:  # Click izquierdo
            self.show()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder and folder not in self.config["folders"]:
            self.config["folders"].append(folder)
            self.list_folders.addItem(folder)
            self.save_config()
            self.add_log(f"Carpeta añadida: {folder}")

    def remove_folder(self):
        selected = self.list_folders.currentRow()
        if selected >= 0:
            folder = self.list_folders.item(selected).text()
            self.config["folders"].remove(folder)
            self.list_folders.takeItem(selected)
            self.save_config()
            self.add_log(f"Carpeta eliminada: {folder}")

    def start_monitoring(self):
        folders = self.config["folders"]
        if not folders:
            QMessageBox.warning(self, "Advertencia", "Añade al menos una carpeta.")
            self.add_log("No hay carpetas para monitorear.")
            return

        try:
            from utils.monitor import FolderMonitorWorker
            self.monitor_worker = FolderMonitorWorker(folders)
            self.monitor_thread = QThread()
            self.monitor_worker.moveToThread(self.monitor_thread)
            self.monitor_thread.started.connect(self.monitor_worker.run)
            self.monitor_worker.log_signal.connect(self.add_log)
            self.monitor_thread.start()

            self.add_log(f"Iniciando monitoreo en {len(folders)} carpeta(s):")
            for folder in folders:
                self.add_log(f"Monitoreando: {folder}")

            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)

        except Exception as e:
            error_msg = f"Error al iniciar monitoreo: {str(e)}"
            self.add_log(error_msg)
            print(error_msg)

    def stop_monitoring(self):
        if self.monitor_worker and hasattr(self.monitor_worker, 'stop'):
            self.monitor_worker.stop()
        if self.monitor_thread:
            self.monitor_thread.quit()
            self.monitor_thread.wait()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.add_log("Monitoreo detenido.")

    def add_log(self, message):
        self.log.addItem(message)
        if self.log.count() > 100:
            self.log.takeItem(0)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.add_log("Configuracion cargada.")
                    return data
            except Exception as e:
                error = f"Error cargando config: {e}"
                print(error)
                self.add_log(error)
        else:
            self.add_log("No se encontro config.json. Usando configuracion vacia.")
        return {"folders": []}

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.add_log("Configuracion guardada.")
        except Exception as e:
            error = f"Error guardando config: {e}"
            print(error)
            self.add_log(error)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage("Notificador", "Sigue ejecutandose en segundo plano.", 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
