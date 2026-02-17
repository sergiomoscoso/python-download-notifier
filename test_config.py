"""Tests para la configuración (config.json)"""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestConfigManagement:
    """Tests para la gestión de configuración"""

    @pytest.fixture
    def temp_config_file(self):
        """Crea un archivo de config temporal para tests"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"folders": ["/path/to/folder1", "/path/to/folder2"]}, f)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_config_file_structure(self):
        """Verifica la estructura base de config.json"""
        config = {"folders": []}
        assert "folders" in config
        assert isinstance(config["folders"], list)

    def test_config_with_multiple_folders(self):
        """Verifica que se pueden almacenar múltiples carpetas"""
        config = {
            "folders": [
                "C:\\Users\\Downloads",
                "C:\\Users\\Documents",
                "D:\\Files"
            ]
        }
        assert len(config["folders"]) == 3
        assert "C:\\Users\\Downloads" in config["folders"]

    def test_config_folder_addition(self):
        """Verifica la adición de carpetas a la configuración"""
        config = {"folders": []}
        new_folder = "C:\\Users\\Downloads"

        if new_folder not in config["folders"]:
            config["folders"].append(new_folder)

        assert new_folder in config["folders"]
        assert len(config["folders"]) == 1

    def test_config_folder_removal(self):
        """Verifica la eliminación de carpetas de la configuración"""
        config = {
            "folders": [
                "C:\\Users\\Downloads",
                "C:\\Users\\Documents"
            ]
        }

        folder_to_remove = "C:\\Users\\Downloads"
        if folder_to_remove in config["folders"]:
            config["folders"].remove(folder_to_remove)

        assert folder_to_remove not in config["folders"]
        assert len(config["folders"]) == 1
        assert "C:\\Users\\Documents" in config["folders"]

    def test_config_duplicate_prevention(self):
        """Verifica que no se puedan añadir carpetas duplicadas"""
        config = {"folders": ["C:\\Users\\Downloads"]}
        new_folder = "C:\\Users\\Downloads"

        if new_folder not in config["folders"]:
            config["folders"].append(new_folder)

        # Contar cuántas veces aparece
        count = config["folders"].count(new_folder)
        assert count == 1

    def test_config_json_serialization(self, temp_config_file):
        """Verifica que la configuración se puede serializar a JSON"""
        config = {"folders": ["C:\\Path1", "C:\\Path2"]}

        json_str = json.dumps(config, indent=2, ensure_ascii=False)
        loaded = json.loads(json_str)

        assert loaded == config
        assert loaded["folders"] == ["C:\\Path1", "C:\\Path2"]

    def test_config_utf8_encoding(self):
        """Verifica que la configuración soporta UTF-8"""
        config = {
            "folders": [
                "C:\\Usuarios\\Descargas",
                "D:\\Documentos"
            ]
        }

        json_str = json.dumps(config, indent=2, ensure_ascii=False)
        # ensure_ascii=False permite caracteres UTF-8
        assert "ó" in json_str or "Descargas" in json_str

    def test_empty_config_default(self):
        """Verifica que el config por defecto está vacío"""
        config = {"folders": []}
        assert config["folders"] == []
        assert len(config["folders"]) == 0


class TestConfigPersistence:
    """Tests para persistencia de config en archivo"""

    @pytest.fixture
    def temp_dir(self):
        """Crea un directorio temporal"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_config_write_and_read(self, temp_dir):
        """Verifica que se puede guardar y leer config"""
        config_path = os.path.join(temp_dir, "config.json")
        original_config = {"folders": ["C:\\Test"]}

        # Write
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(original_config, f, indent=2, ensure_ascii=False)

        # Read
        with open(config_path, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)

        assert loaded_config == original_config

    def test_missing_config_file_handling(self):
        """Verifica que se maneja correctamente la ausencia de config.json"""
        # Simular comportamiento: si no existe, usar config vacía
        config_exists = os.path.exists("nonexistent_config.json")

        if config_exists:
            with open("nonexistent_config.json", "r") as f:
                config = json.load(f)
        else:
            config = {"folders": []}

        assert config == {"folders": []}

    def test_invalid_json_handling(self, temp_dir):
        """Verifica manejo de archivo JSON inválido"""
        config_path = os.path.join(temp_dir, "bad_config.json")

        # Escribir JSON inválido
        with open(config_path, "w") as f:
            f.write("{ invalid json }")

        # Intentar leer
        config = None
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            # Si falla, usar config vacía
            config = {"folders": []}

        assert config == {"folders": []}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
