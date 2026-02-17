"""Tests para el módulo monitor.py"""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from monitor import TEMP_EXT, MonitorHandler


class TestMonitorHandler:
    """Tests para la clase MonitorHandler"""

    def setup_method(self):
        """Setup antes de cada test"""
        self.callback = Mock()
        self.handler = MonitorHandler(self.callback, "test_folder")

    def test_handler_initialization(self):
        """Verifica que el handler se inicializa correctamente"""
        assert self.handler.callback == self.callback
        assert self.handler.folder_name == "test_folder"

    def test_on_created_final_file(self):
        """Verifica que detecta archivos finales al crear"""
        # Mock event para un archivo .pdf
        event = Mock()
        event.is_directory = False
        event.src_path = "/downloads/documento.pdf"

        self.handler.on_created(event)

        # El callback debe ser llamado
        self.callback.assert_called_once()
        args = self.callback.call_args
        assert "documento.pdf" in str(args)

    def test_on_created_temp_file_not_detected(self):
        """Verifica que NO detecta archivos temporales al crear"""
        event = Mock()
        event.is_directory = False
        event.src_path = "/downloads/file.pdf.crdownload"

        self.handler.on_created(event)

        # El callback NO debe ser llamado
        self.callback.assert_not_called()

    def test_on_created_directory_ignored(self):
        """Verifica que ignora directorios"""
        event = Mock()
        event.is_directory = True
        event.src_path = "/downloads/newfolder"

        self.handler.on_created(event)

        # El callback NO debe ser llamado
        self.callback.assert_not_called()

    def test_on_created_hidden_file_ignored(self):
        """Verifica que ignora archivos ocultos"""
        event = Mock()
        event.is_directory = False
        event.src_path = "/downloads/.hidden_file"

        self.handler.on_created(event)

        # El callback NO debe ser llamado
        self.callback.assert_not_called()

    def test_on_moved_final_file(self):
        """Verifica que detecta cuando archivo temporal se renombra a final"""
        event = Mock()
        event.is_directory = False
        event.dest_path = "/downloads/document.pdf"

        self.handler.on_moved(event)

        # El callback debe ser llamado
        self.callback.assert_called_once()
        args = self.callback.call_args
        assert "document.pdf" in str(args)

    def test_on_moved_temp_file_ignored(self):
        """Verifica que ignora archivos que siguen siendo temporales"""
        event = Mock()
        event.is_directory = False
        event.dest_path = "/downloads/file.part"

        self.handler.on_moved(event)

        # El callback NO debe ser llamado
        self.callback.assert_not_called()

    @pytest.mark.parametrize("temp_ext", TEMP_EXT)
    def test_all_temp_extensions_ignored(self, temp_ext):
        """Verifica que TODAS las extensiones temporales son ignoradas"""
        event = Mock()
        event.is_directory = False
        event.src_path = f"/downloads/file{temp_ext}"

        self.handler.on_created(event)
        self.callback.assert_not_called()

    def test_case_insensitive_extension_detection(self):
        """Verifica que la detección es insensible a mayúsculas"""
        # Test con .TMP (mayúsculas)
        event = Mock()
        event.is_directory = False
        event.src_path = "/downloads/file.TMP"

        self.handler.on_created(event)
        self.callback.assert_not_called()

        # Reset mock
        self.callback.reset_mock()

        # Test con .PDF (mayúsculas)
        event.src_path = "/downloads/file.PDF"
        self.handler.on_created(event)
        self.callback.assert_called_once()


class TestTempExtensionsList:
    """Tests para la lista de extensiones temporales"""

    def test_common_temp_extensions_present(self):
        """Verifica que las extensiones comunes están en la lista"""
        expected = [".tmp", ".crdownload", ".part"]
        for ext in expected:
            assert ext in TEMP_EXT

    def test_temp_ext_list_not_empty(self):
        """Verifica que TEMP_EXT no está vacío"""
        assert len(TEMP_EXT) > 0

    def test_temp_ext_all_lowercase(self):
        """Verifica que todas las extensiones están en minúsculas"""
        for ext in TEMP_EXT:
            assert ext == ext.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
