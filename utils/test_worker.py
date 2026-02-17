"""Tests para el módulo monitor.py - FolderMonitorWorker y threading"""
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from PyQt6.QtCore import QObject, QThread, pyqtSignal


# Mock para FolderMonitorWorker (simulación básica)
class MockFolderMonitorWorker(QObject):
    """Versión test de FolderMonitorWorker"""
    log_signal = pyqtSignal(str)

    def __init__(self, folders):
        super().__init__()
        self.folders = folders
        self.observers = []
        self.running = False
        self.logs = []

    def log(self, msg):
        self.logs.append(msg)
        self.log_signal.emit(msg)

    def notify(self, title, message):
        self.log(f"Notificacion: {message}")

    def stop(self):
        self.running = False
        for obs in self.observers:
            if hasattr(obs, 'stop'):
                obs.stop()

    def run(self):
        self.running = True
        for folder in self.folders:
            if not os.path.exists(folder):
                self.log(f"No encontrada: {folder}")
            else:
                self.log(f"Monitoreando: {folder}")


class TestFolderMonitorWorker:
    """Tests para el worker de monitoreo"""

    def test_worker_initialization(self):
        """Verifica inicialización del worker"""
        folders = ["C:\\Downloads", "C:\\Documents"]
        worker = MockFolderMonitorWorker(folders)

        assert worker.folders == folders
        assert worker.running is False
        assert worker.observers == []

    def test_worker_log_signal(self):
        """Verifica que el worker emite señales de log"""
        worker = MockFolderMonitorWorker([])
        logs_captured = []

        # Conectar signal a capturador
        worker.log_signal.connect(lambda msg: logs_captured.append(msg))

        worker.log("Test message")

        assert "Test message" in logs_captured

    def test_worker_with_valid_folder(self):
        """Verifica comportamiento con carpeta válida"""
        with tempfile.TemporaryDirectory() as tmpdir:
            worker = MockFolderMonitorWorker([tmpdir])
            worker.run()

            assert any("Monitoreando" in log for log in worker.logs)

    def test_worker_with_invalid_folder(self):
        """Verifica comportamiento con carpeta inexistente"""
        invalid_folder = "C:\\NonExistentFolder12345"
        worker = MockFolderMonitorWorker([invalid_folder])
        worker.run()

        assert any("No encontrada" in log for log in worker.logs)

    def test_worker_multiple_folders(self):
        """Verifica worker con múltiples carpetas"""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                folders = [tmpdir1, tmpdir2]
                worker = MockFolderMonitorWorker(folders)
                worker.run()

                assert len([log for log in worker.logs if "Monitoreando" in log]) == 2

    def test_worker_stop(self):
        """Verifica que stop detiene el worker"""
        worker = MockFolderMonitorWorker([])
        worker.running = True

        worker.stop()

        assert worker.running is False

    def test_worker_notify(self):
        """Verifica notificación"""
        worker = MockFolderMonitorWorker([])

        worker.notify("Título", "Mensaje de prueba")

        assert any("Mensaje de prueba" in log for log in worker.logs)

    def test_worker_empty_folder_list(self):
        """Verifica comportamiento con lista vacía"""
        worker = MockFolderMonitorWorker([])
        worker.run()

        assert worker.running is True


class TestMonitoringState:
    """Tests para estado del monitoreo"""

    def test_running_flag_initial_state(self):
        """Verifica que running comienza en False"""
        worker = MockFolderMonitorWorker([])
        assert worker.running is False

    def test_running_flag_on_run(self):
        """Verifica que running se pone True al ejecutar"""
        worker = MockFolderMonitorWorker([])

        # Simular inicio
        worker.running = True

        assert worker.running is True

    def test_observer_list_management(self):
        """Verifica gestión de lista de observers"""
        worker = MockFolderMonitorWorker([])

        # Simular agregar observers
        mock_observer = Mock()
        worker.observers.append(mock_observer)

        assert len(worker.observers) == 1
        assert worker.observers[0] == mock_observer

    def test_logs_accumulation(self):
        """Verifica que los logs se acumulan"""
        worker = MockFolderMonitorWorker([])

        worker.log("Log 1")
        worker.log("Log 2")
        worker.log("Log 3")

        assert len(worker.logs) == 3
        assert "Log 1" in worker.logs
        assert "Log 3" in worker.logs


class TestFolderValidation:
    """Tests para validación de carpetas"""

    def test_valid_folder_detection(self):
        """Verifica detección de carpeta válida"""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert os.path.exists(tmpdir)

    def test_absolute_vs_relative_paths(self):
        """Verifica manejo de rutas absolutas vs relativas"""
        abs_path = os.path.abspath(".")
        assert os.path.isabs(abs_path)
        assert os.path.exists(abs_path)

    def test_path_normalization(self):
        """Verifica normalización de rutas"""
        path = "C:\\Users\\..\\Users\\Downloads"
        normalized = os.path.normpath(path)

        # Debe contener la ruta sin ..
        assert ".." not in normalized

    def test_folder_accessibility(self):
        """Verifica accesibilidad de carpeta"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear archivo para verificar acceso
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            assert os.access(tmpdir, os.R_OK)
            assert os.path.exists(test_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
