"""Secure configuration management for the application"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    # Try to load from project root
    load_dotenv()


class Config:
    """Base configuration - should not contain secrets"""
    
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    APP_NAME = os.getenv("APP_NAME", "Notificador de Descargas")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_debug(cls) -> bool:
        """Get debug status safely"""
        debug = cls.DEBUG
        if debug and cls.APP_ENV == "production":
            raise ValueError("❌ DEBUG cannot be True in production!")
        return debug
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.APP_ENV == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development"""
        return cls.APP_ENV == "development"


class SecureConfig(Config):
    """Secure configuration with validation"""
    
    @staticmethod
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Safely retrieve a secret from environment variables.
        
        ⚠️ IMPORTANT: Never log or print secrets!
        
        Args:
            key: Environment variable name
            default: Default value if key not found
            
        Returns:
            Secret value or default
            
        Raises:
            ValueError: If secret is required but not found
        """
        value = os.getenv(key, default)
        
        if value is None and key in ["SECRET_KEY", "API_KEY", "DB_PASSWORD"]:
            raise ValueError(
                f"❌ Required secret '{key}' not found in environment. "
                f"Add it to your .env file (not .env.example)"
            )
        
        return value
    
    @staticmethod
    def validate_env() -> bool:
        """
        Validate that required environment variables are set correctly.
        
        Returns:
            True if all validations pass
            
        Raises:
            ValueError: If validation fails
        """
        env = os.getenv("APP_ENV", "development")
        
        # Production-specific validations
        if env == "production":
            required = ["SECRET_KEY", "API_KEY"]
            for key in required:
                if not os.getenv(key):
                    raise ValueError(
                        f"❌ Production requires '{key}' in .env file"
                    )
            
            if os.getenv("DEBUG", "false").lower() == "true":
                raise ValueError(
                    "❌ DEBUG must be 'false' in production"
                )
        
        return True


# Initialize configuration
config = SecureConfig()

# Validation on import
try:
    SecureConfig.validate_env()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
