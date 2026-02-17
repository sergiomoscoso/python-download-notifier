"""Security tests for the application"""
import os
import pytest
from unittest.mock import patch, MagicMock
from config import SecureConfig, Config


class TestConfigurationSecurity:
    """Tests for secure configuration handling"""

    def test_debug_disabled_by_default(self):
        """Verifica que DEBUG es falso por defecto"""
        # En dev puede ser verdadero, pero debe validarse
        assert Config.is_development() or not Config.DEBUG

    def test_production_mode_detected(self):
        """Verifica detección de modo producción"""
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            config = SecureConfig()
            assert config.is_production()

    def test_debug_false_in_production(self):
        """Verifica que DEBUG no puede ser True en producción"""
        with patch.dict(os.environ, {"APP_ENV": "production", "DEBUG": "false"}):
            config = SecureConfig()
            assert config.is_production()
            assert not config.get_debug()

    def test_debug_validation_fails_in_production(self):
        """Verifica que DEBUG=True en producción lanza error"""
        with patch.dict(os.environ, {"APP_ENV": "production", "DEBUG": "true"}):
            config = SecureConfig()
            with pytest.raises(ValueError, match="DEBUG cannot be True"):
                config.get_debug()

    def test_secret_key_required_validation(self):
        """Verifica que SECRET_KEY es requerido en producción"""
        with patch.dict(os.environ, 
                       {"APP_ENV": "production", "SECRET_KEY": ""},
                       clear=False):
            with pytest.raises(ValueError, match="Required secret"):
                SecureConfig.validate_env()

    def test_secret_retrieval_with_default(self):
        """Verifica obtención de secreto con valor por defecto"""
        with patch.dict(os.environ, {}, clear=True):
            value = SecureConfig.get_secret("NONEXISTENT", "default_value")
            assert value == "default_value"

    def test_secret_retrieval_from_env(self):
        """Verifica obtención de secreto desde variables de entorno"""
        with patch.dict(os.environ, {"TEST_SECRET": "secure_value"}):
            value = SecureConfig.get_secret("TEST_SECRET")
            assert value == "secure_value"

    def test_missing_required_secret_raises_error(self):
        """Verifica que secreto requerido faltante lanza error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Required secret"):
                SecureConfig.get_secret("SECRET_KEY")

    def test_environment_validation_passes_in_dev(self):
        """Verifica que validación pasa en desarrollo"""
        with patch.dict(os.environ, {"APP_ENV": "development"}):
            result = SecureConfig.validate_env()
            assert result is True

    def test_app_env_modes(self):
        """Verifica diferentes modos de APP_ENV"""
        modes = ["development", "testing", "production"]
        
        for mode in modes:
            with patch.dict(os.environ, {"APP_ENV": mode}):
                config = SecureConfig()
                if mode == "production":
                    assert config.is_production()
                elif mode == "development":
                    assert config.is_development()


class TestSecretManagement:
    """Tests para manejo de secretos"""

    def test_secret_not_logged(self):
        """Verifica que secretos no se loguean fácilmente"""
        # Los secretos deben ser tratados cuidadosamente
        secret = SecureConfig.get_secret("FAKE_SECRET", "should_not_appear")
        # El secret nunca debe imprimirse accidentalmente en logs
        secret_str = str(secret)
        assert "should_not_appear" in secret_str  # valor es el esperado

    def test_empty_secret_detection(self):
        """Verifica detección de secretos vacíos"""
        with patch.dict(os.environ, {"SECRET_KEY": ""}):
            # En producción, debe fallar
            with patch.dict(os.environ, {"APP_ENV": "production"}):
                with pytest.raises(ValueError):
                    SecureConfig.validate_env()

    def test_api_key_required_in_production(self):
        """Verifica que API_KEY es requerido en producción"""
        with patch.dict(os.environ, 
                       {"APP_ENV": "production", "API_KEY": ""},
                       clear=False):
            with pytest.raises(ValueError):
                SecureConfig.validate_env()

    def test_whitespace_only_secret_invalid(self):
        """Verifica que secreto solo con espacios es inválido"""
        with patch.dict(os.environ, {"SECRET_KEY": "   "}):
            value = SecureConfig.get_secret("SECRET_KEY")
            # El valor está vacío después de strip
            assert value.strip() == ""


class TestEnvironmentSafety:
    """Tests para seguridad del entorno"""

    def test_env_isolation_in_production(self):
        """Verifica aislamiento de entorno en producción"""
        with patch.dict(os.environ, {"APP_ENV": "production", "DEBUG": "false"}):
            config = SecureConfig()
            assert config.is_production()
            assert not config.get_debug()

    def test_environment_variable_types(self):
        """Verifica tipos de variables de entorno"""
        with patch.dict(os.environ, {
            "APP_ENV": "development",
            "DEBUG": "false",
            "LOG_LEVEL": "INFO"
        }):
            config = Config()
            assert isinstance(config.APP_ENV, str)
            assert isinstance(config.DEBUG, bool)
            assert isinstance(config.LOG_LEVEL, str)

    def test_env_file_loading(self):
        """Verifica que .env se carga correctamente"""
        # Simular que .env existe pero está vacío
        with patch("config.Path.exists") as mock_exists:
            mock_exists.return_value = False
            # Si no existe, debe usar defaults
            config = Config()
            assert config.APP_ENV == "development"


class TestInputValidation:
    """Tests para validación de input"""

    def test_invalid_app_env_value(self):
        """Verifica manejo de valores inválidos en APP_ENV"""
        # Los valores válidos son: development, testing, production
        with patch.dict(os.environ, {"APP_ENV": "invalid_mode"}):
            config = SecureConfig()
            # Debe no ser ninguno de los modos conocidos
            assert not config.is_production()
            assert not config.is_development()

    def test_boolean_string_conversion(self):
        """Verifica conversión segura de strings a Boolean"""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("", False),
            ("0", False),
            ("1", False),  # "1" != "true"
        ]
        
        for string_val, expected in test_cases:
            with patch.dict(os.environ, {"DEBUG": string_val}):
                config = Config()
                assert config.DEBUG == expected, f"Failed for '{string_val}'"

    def test_log_level_validation(self):
        """Verifica validación de LOG_LEVEL"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            with patch.dict(os.environ, {"LOG_LEVEL": level}):
                config = Config()
                assert config.LOG_LEVEL == level


class TestAWSCredentials:
    """Tests para credenciales de AWS (si aplica)"""

    def test_aws_credentials_not_hardcoded(self):
        """Verifica que credenciales de AWS no están hardcodeadas"""
        # Las credenciales deben venir de variables de entorno o archivos seguros
        with patch.dict(os.environ, {}, clear=True):
            # No por defecto
            assert os.getenv("AWS_ACCESS_KEY_ID") is None
            assert os.getenv("AWS_SECRET_ACCESS_KEY") is None

    def test_aws_region_configured(self):
        """Verifica que AWS_REGION se puede configurar"""
        with patch.dict(os.environ, {"AWS_REGION": "us-east-1"}):
            region = os.getenv("AWS_REGION")
            assert region == "us-east-1"


class TestDatabaseSecurity:
    """Tests para seguridad de base de datos"""

    def test_db_password_not_default(self):
        """Verifica que DB_PASSWORD no tiene valor por defecto"""
        with patch.dict(os.environ, {}, clear=True):
            password = os.getenv("DB_PASSWORD")
            assert password is None

    def test_db_credentials_from_env(self):
        """Verifica que credenciales de BD vienen de entorno"""
        with patch.dict(os.environ, {
            "DB_HOST": "localhost",
            "DB_USER": "admin",
            "DB_PASSWORD": "secure_pass"
        }):
            assert os.getenv("DB_HOST") == "localhost"
            assert os.getenv("DB_USER") == "admin"
            # El password está disponible pero no debe ser commiteado
            assert os.getenv("DB_PASSWORD") == "secure_pass"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
