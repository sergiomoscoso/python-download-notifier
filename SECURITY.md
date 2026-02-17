# 🔒 Security Policy & Guidelines

## Documento Oficial de Seguridad para File Notifier

**Última actualización:** Febrero 2026
**Versión:** 1.0
**Responsable:** Equipo de Desarrollo

---

## 📋 Tabla de Contenidos

1. [Visión General de Seguridad](#-visión-general-de-seguridad)
2. [Normas OWASP Implementadas](#-normas-owasp-implementadas)
3. [Políticas de Seguridad](#-políticas-de-seguridad)
4. [Gestión de Secretos](#-gestión-de-secretos)
5. [Vulnerabilidades en Dependencias](#-vulnerabilidades-en-dependencias)
6. [Prevención de Ataques Comunes](#-prevención-de-ataques-comunes)
7. [Proceso de Diseño Seguro](#-proceso-de-diseño-seguro)
8. [Reportar Vulnerabilidades](#-reportar-vulnerabilidades)
9. [Checklist Pre-Release](#-checklist-pre-release)
10. [Roadmap de Seguridad](#-roadmap-de-seguridad)

---

## 🎯 Visión General de Seguridad

### Compromiso
File Notifier es desarrollado con **seguridad by design**. Implementamos validaciones automáticas, escaneo de dependencias y análisis estático de código en cada cambio.

### Niveles de Seguridad

| Nivel | Aplicación | Herramientas |
|-------|-----------|-------------|
| **Nivel 1: Local** | Desarrollo personal | bandit, black, flake8 |
| **Nivel 2: Pre-commit** | Antes de cada commit | pre-commit hooks, detect-secrets |
| **Nivel 3: Dependencias** | Verificación de paquetes | pip-audit, safety |
| **Nivel 4: Tests** | Validación de lógica | test_security.py (64 tests) |
| **Nivel 5: CI/CD** | En servidor (GitHub Actions) | *Preparado para implementación* |

### Principios Fundamentales

✅ **Defensa en profundidad**: Múltiples capas de validación
✅ **Principio de menor privilegio**: Acceso solo a recursos necesarios
✅ **Fail secure**: En caso de error, comportamiento seguro por defecto
✅ **Auditoría y logging**: Registro de eventos importantes
✅ **Transparencia**: Documentación completa de prácticas de seguridad

---

## 🛡️ Normas OWASP Implementadas

### OWASP Top 10 (2021)

#### 1. **Inyección SQL** ✅
- **Status**: N/A - Aplicación no usa BD directamente
- **Mitigación**: Si se implementa, usar ORMs con prepared statements
- **Test**: Validación en test_security.py

#### 2. **Fallos de autenticación** ✅
- **Status**: Implementado parcialmente
- **Mitigación**:
  - Validación de credenciales en config.py
  - Segregación de secrets vs configuración pública
  - Tests en test_security.py::TestConfigurationSecurity
- **Ejemplo**:
  ```python
  # ❌ MAL - nunca hacer esto
  password = "hardcoded_password"

  # ✅ BIEN - usar variables de entorno
  password = SecureConfig.get_secret("DB_PASSWORD")
  ```

#### 3. **Exposición de datos sensibles** ✅
- **Status**: CRÍTICO - Implementado
- **Mitigación**:
  - `.gitignore` previene commit de `.env`
  - `detect-secrets` detecta strings de alta entropía
  - `.env.example` es plantilla sin valores reales
- **Verificar**:
  ```bash
  # Buscar secretos accidentales
  python -m detect-secrets scan --all-files
  ```

#### 4. **Entidades externas XML (XXE)** ✅
- **Status**: N/A - No se parsea XML
- **Mitigación**: Si se agrega, usar parsers seguros

#### 5. **Control de acceso roto** ✅
- **Status**: Implementado
- **Mitigación**:
  - Separación clara de carpetas de configuración
  - Permisos de archivo sobre variables sensibles
  - Validación de modo producción vs desarrollo

#### 6. **Configuración de seguridad incorrecta** ✅
- **Status**: CRÍTICO - Implementado
- **Mitigación**:
  - Config de seguridad centralizada en config.py
  - Validación automática en SecureConfig.validate_env()
  - DEBUG=false requerido en producción
  - Tests en test_security.py::TestConfigurationSecurity

#### 7. **XSS (Cross-Site Scripting)** ✅
- **Status**: N/A - Aplicación de escritorio (no web)
- **Mitigación**: Seria en versión web futura

#### 8. **Deserialization insegura** ✅
- **Status**: Implementado
- **Mitigación**:
  - JSON parsing seguro (no pickle)
  - Validación de estructura en test_config.py
- **Ejemplo**:
  ```python
  # ✅ BIEN - JSON seguro
  config = json.load(f)

  # ❌ MAL - nunca usar pickle con datos no confiables
  config = pickle.load(f)
  ```

#### 9. **Logging y monitoreo insuficiente** ✅
- **Status**: Preparado
- **Mitigación**:
  - Sistema de logging en main.py
  - Variables de entorno para configurar niveles (LOG_LEVEL)
  - Sentry preparado para producción (ver Roadmap)

#### 10. **SSRF (Server-Side Request Forgery)** ✅
- **Status**: N/A - Aplicación local
- **Mitigación**: Sera crítico si se agrega API externa

---

## 🔐 Políticas de Seguridad

### 1. Gestión de Secretos

**NUNCA commit:**
- `.env` (archivo de variables reales)
- Claves privadas (`*.key`, `*.pem`)
- Tokens de API
- Credenciales de base de datos

**SÍ commit:**
- `.env.example` (plantilla vacía)
- `.gitignore` (especifica qué no commitear)
- `config.py` (lógica de carga segura)

**Validación automática:**
```bash
# Pre-commit hook automático ejecuta:
python -m detect-secrets scan --all-files

# Genera reporte:
python -m detect-secrets scan --all-files --baseline .secrets.baseline
```

### 2. Estándares de Código

Todos los commits se validan con:

```bash
# Seguridad
python -m bandit -r . -c .bandit

# Formato (auto-fix)
python -m black .

# Imports
python -m isort .

# Linting
python -m flake8 --max-line-length=100

# Tipos
python -m mypy .
```

### 3. Dependencias

**Escaneo automático en pre-commit:**
```bash
# Vulnerabilidades conocidas
python -m pip_audit

# Segundo escaneo
python -m safety check
```

**Reporte esperado:**
```
✓ No known vulnerabilities found
✓ No insecure package versions detected
```

### 4. Versionado

- `MAJOR`: Cambios incompatibles (especialmente seguridad)
- `MINOR`: Nuevas características (incluyendo validaciones)
- `PATCH`: Bug fixes de seguridad críticos

**Ejemplo:** `v1.2.5` = Mayor:Menor:Patch

---

## 🔑 Gestión de Secretos

### Archivo .env

**Ubicación:** `~/.env` (no commiteado)

**Estructura segura:**
```bash
# .env (LOCAL ONLY - NEVER COMMIT)
APP_ENV=production
SECRET_KEY=your-super-secret-key-here-very-random
API_KEY=abc123def456ghi789
DB_PASSWORD=very_secure_password_123
```

### Acceso Seguro en Código

```python
from config import SecureConfig

# ✅ BIEN
secret = SecureConfig.get_secret("SECRET_KEY")

# ❌ MAL
import os
secret = os.getenv("SECRET_KEY")  # Sin validación
```

### Por Entorno

**Development (.env.development):**
```
APP_ENV=development
DEBUG=true
SECRET_KEY=dev-key-not-secret
```

**Production (.env.production):**
```
APP_ENV=production
DEBUG=false
SECRET_KEY=prod-key-super-secret-random-64-chars
```

---

## 🔍 Vulnerabilidades en Dependencias

### Escaneo de Seguridad

**Comando para verificar:**
```bash
# Opción 1: pip-audit
python -m pip_audit

# Opción 2: safety
python -m safety check

# Opción 3: Ambas (recomendado)
python -m pip_audit && python -m safety check
```

### Actualizar Dependencias Seguras

```bash
# Ver actualizaciones disponibles
pip list --outdated

# Actualizar con seguridad
pip install --upgrade package_name

# Re-ejecutar escaneo
python -m pip_audit
```

### Política de Actualización

- **Critical**: Dentro de 24 horas
- **High**: Dentro de 1 semana
- **Medium**: Dentro de 2 semanas
- **Low**: Próxima release

### Historico de Scanning

Mantener registro en `security-scans/`:

```
security-scans/
├── 2026-02-17_pip_audit.json
├── 2026-02-17_safety.json
└── 2026-02-17_bandit.json
```

---

## 🛡️ Prevención de Ataques Comunes

### 1. Inyección de Comandos

**❌ Malo:**
```python
import os
user_input = "file.txt; rm -rf /"
os.system(f"process {user_input}")  # VULNERABILIDAD
```

**✅ Bueno:**
```python
import subprocess
result = subprocess.run(["process", user_input], capture_output=True)
```

### 2. Path Traversal

**❌ Malo:**
```python
user_path = request.args.get("file")
with open(user_path) as f:  # ¿Qué si user_path = "../../etc/passwd"?
    return f.read()
```

**✅ Bueno:**
```python
from pathlib import Path
base_dir = Path("/safe/folder")
requested = base_dir / user_path
# Asegurar que está dentro de base_dir
requested.resolve().relative_to(base_dir.resolve())
```

### 3. Race Conditions

**En monitor.py:**
```python
# ✅ Ya implementado
# Watchdog detecta de forma atómica
if not filename.startswith("."):
    self.callback(...)  # Safe
```

### 4. Desbordamiento de Buffer

**❌ Malo:**
```python
large_input = "A" * 1000000
store_in_memory(large_input)  # Crash
```

**✅ Bueno:**
```python
if len(user_input) > MAX_LENGTH:
    raise ValueError("Input too large")
```

---

## 📐 Proceso de Diseño Seguro

### Antes de codificar

1. **Threat Model**: ¿Quién puede atacar esto?
2. **OWASP Review**: ¿Qué vulnerabilidades aplican?
3. **Data Classification**: ¿Qué es sensible?
4. **Security Requirements**: ¿Qué debo proteger?

### Checklist de Codificación

- [ ] Validar TODO usuario input
- [ ] Usar librerías estándar, no reinventar criptografía
- [ ] Logging de eventos de seguridad
- [ ] Manejo seguro de errores (no revelar internals)
- [ ] Principio de menor privilegio
- [ ] Tests de seguridad escritos

### Antes de Release

Ver [Checklist Pre-Release](#-checklist-pre-release)

---

## 🔴 Reportar Vulnerabilidades

### Responsabilidad Compartida

Si descubres una vulnerabilidad:

**NO PUBLIQUES en GitHub/Internet**

**CONTACTA:**
1. Email: security@company.local
2. Asunto: `[SECURITY] Descripción breve`
3. Incluye:
   - Descripción detallada
   - Pasos para reproducir
   - Impacto potencial
   - Sugerencia de fix (si tienes)

### Proceso de Respuesta

| Tiempo | Acción |
|--------|--------|
| **0-24h** | Confirmación de recepción |
| **1-7 días** | Análisis e investigación |
| **7-30 días** | Fix y testing |
| **30+ días** | Release con patch |

### Divulgación Responsable

Nos comprometemos a:
- ✅ Investigar todas las reportes seriamente
- ✅ Mantener confidencialidad
- ✅ Proporcionar actualizaciones regulares
- ✅ Creditar al reportador (si lo desea)
- ✅ No tomar acciones legales contra reportadores in-good-faith

---

## ✅ Checklist Pre-Release

**Ejecutar 24 horas antes de release:**

```bash
# 1. Análisis estático de seguridad
echo "=== BANDIT (Security Linting) ==="
python -m bandit -r . -c .bandit
# Resultado esperado: No issues found

# 2. Escaneo de dependencias
echo "=== PIP-AUDIT (Dependency Vulnerabilities) ==="
python -m pip_audit
# Resultado esperado: No known vulnerabilities found

# 3. Segundo escaneo de dependencias
echo "=== SAFETY (Dependency Check) ==="
python -m safety check
# Resultado esperado: No known security vulnerabilities

# 4. Validación de secretos
echo "=== DETECT-SECRETS (Secret Detection) ==="
python -m detect-secrets scan --all-files
# Resultado esperado: No secrets detected

# 5. Tests de seguridad
echo "=== SECURITY TESTS ==="
pytest test_security.py -v
# Resultado esperado: All tests passed

# 6. Cobertura de tests
echo "=== TEST COVERAGE ==="
pytest --cov=. --cov-report=term-missing
# Resultado esperado: >80% coverage

# 7. Formato y linting
echo "=== CODE QUALITY ==="
python -m black --check .
python -m isort --check-only .
python -m flake8 .
# Resultado esperado: No errors
```

**Checklist Manual:**

- [ ] `.env` NO está commiteado
- [ ] `.env.example` tiene comentarios pero SIN valores reales
- [ ] `DEBUG = false` en producción
- [ ] Todas las dependencias están pinned en requirements.txt
- [ ] Cambios de seguridad documentados en CHANGELOG
- [ ] Release notes mencionan parches de seguridad
- [ ] Cambios probados en ambiente similar a producción

**Documento de Release:**

```markdown
## Release v1.2.3 - [Fecha]

### Security Updates
- Fixed [CVE-ID]: [Descripción]
- Updated dependencies: [Lista]
- Implemented [Característica de seguridad]

### Breaking Changes
- [Lista de cambios incompatibles]

### Contributors
- [Nombres]
```

---

## 🚀 Roadmap de Seguridad

### Fase 1: Localidad (✅ COMPLETADO)
- [x] Bandit + flake8
- [x] Pre-commit hooks
- [x] Config management
- [x] Tests de seguridad
- [x] Documentación SECURITY.md

### Fase 2: CI/CD (Q2 2026)
- [ ] GitHub Actions con escaneo automático
- [ ] Branch protection rules
- [ ] Required approvals para PRs
- [ ] Automated dependency updates (Dependabot)

### Fase 3: Enterprise (Q3 2026)
- [ ] Snyk integration para monitoreo continuo
- [ ] SonarQube para análisis avanzado
- [ ] Sentry para error tracking en producción
- [ ] SBOM (Software Bill of Materials)

### Fase 4: Compliance (Q4 2026)
- [ ] OWASP compliance report
- [ ] ISO 27001 readiness
- [ ] GDPR compliance (si es relevante)
- [ ] Audit logs completos

---

## 📚 Referencias

### Documentación Externa

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security](https://www.python.org/dev/peps/pep-0619/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

### Herramientas Usadas

- [Bandit](https://bandit.readthedocs.io/) - Security linter
- [pip-audit](https://pypi.org/project/pip-audit/) - Dependency vulnerabilities
- [Safety](https://pypi.org/project/safety/) - Dependency check
- [detect-secrets](https://pypi.org/project/detect-secrets/) - Secret detection
- [pre-commit](https://pre-commit.com/) - Git hooks framework

### Documentos Internos

- [TESTING.md](./TESTING.md) - Test suite documentation
- [config.py](./config.py) - Secure configuration module
- [test_security.py](./test_security.py) - Security tests

---

## 📞 Contacto

**Responsable de Seguridad:** [Tu nombre/equipo]
**Email:** security@company.local
**Urgencias:** [Teléfono/Slack]

---

## 📄 Control de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-02-17 | Documento inicial - Security framework completo |

---

**Última revisión:** 2026-02-17
**Próxima revisión:** 2026-05-17
**Estado:** ✅ ACTIVO
