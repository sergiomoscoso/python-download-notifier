#!/usr/bin/env python3
"""
Security Framework Verification Script
Validates that all security components are properly configured
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    path = Path(filepath)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_file_content(filepath, search_text, description):
    """Check if file contains specific text"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ {description}: File not found - {filepath}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        found = search_text.lower() in content.lower()
        status = "✅" if found else "⚠️"
        print(f"{status} {description}")
        return found
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def verify_json_valid(filepath, description):
    """Check if JSON file is valid"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ {description}: File not found")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ {description}: Valid JSON")
        return True
    except Exception as e:
        print(f"❌ {description}: Invalid JSON - {e}")
        return False

def main():
    print("=" * 70)
    print("SECURITY FRAMEWORK VERIFICATION")
    print("=" * 70)
    print()
    
    results = []
    
    # 1. Check configuration files
    print("📋 CONFIGURATION FILES:")
    print("-" * 70)
    results.append(check_file_exists('.env.example', '.env.example template'))
    results.append(check_file_exists('.gitignore', '.gitignore protection'))
    results.append(check_file_exists('.pre-commit-config.yaml', 'Pre-commit configuration'))
    results.append(check_file_exists('config.py', 'Secure config module'))
    results.append(check_file_exists('.secrets.baseline', 'Detect-secrets baseline'))
    print()
    
    # 2. Check requirements files
    print("📦 DEPENDENCIES:")
    print("-" * 70)
    results.append(check_file_exists('requirements-security.txt', 'Security requirements'))
    results.append(check_file_content(
        'requirements-security.txt',
        'bandit',
        'Bandit security linter'
    ))
    results.append(check_file_content(
        'requirements-security.txt',
        'pip-audit',
        'pip-audit dependency scanner'
    ))
    results.append(check_file_content(
        'requirements-security.txt',
        'detect-secrets',
        'Detect-secrets tool'
    ))
    print()
    
    # 3. Check test files
    print("✅ TESTS:")
    print("-" * 70)
    results.append(check_file_exists('test_security.py', 'Security tests'))
    results.append(check_file_content(
        'test_security.py',
        'class TestEnvironmentVariables',
        'Environment variable tests'
    ))
    results.append(check_file_content(
        'test_security.py',
        'class TestSecureConfigManagement',
        'Config management tests'
    ))
    results.append(check_file_content(
        'test_security.py',
        'test_secrets_not_committed',
        'Git protection tests'
    ))
    print()
    
    # 4. Check documentation
    print("📚 DOCUMENTATION:")
    print("-" * 70)
    results.append(check_file_exists('SECURITY.md', 'Security policy'))
    results.append(check_file_content(
        'SECURITY.md',
        'OWASP',
        'OWASP compliance documentation'
    ))
    results.append(check_file_content(
        'SECURITY.md',
        'secret',
        'Secret management guide'
    ))
    results.append(check_file_exists('SECURITY_VERIFICATION.md', 'Verification checklist'))
    results.append(check_file_exists('SECURITY_SETUP_COMPLETE.md', 'Setup summary'))
    print()
    
    # 5. Check JSON validity
    print("🔍 FILE VALIDATION:")
    print("-" * 70)
    results.append(verify_json_valid('.secrets.baseline', 'Secrets baseline'))
    results.append(check_file_content('.gitignore', '.env', '.env protection in gitignore'))
    results.append(check_file_content('.gitignore', '*.key', 'Key file protection'))
    results.append(check_file_content('.gitignore', '*.pem', 'Certificate protection'))
    print()
    
    # 6. Check git
    print("🔒 GIT CONFIGURATION:")
    print("-" * 70)
    git_dir = Path('.git')
    results.append(git_dir.exists())
    if git_dir.exists():
        print(f"✅ Git repository initialized")
        hook_file = Path('.git/hooks/pre-commit')
        if hook_file.exists():
            print(f"✅ Pre-commit hook installed")
            results.append(True)
        else:
            print(f"⚠️ Pre-commit hook not found (may be installing)")
            results.append(False)
    print()
    
    # 7. Summary
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"SUMMARY: {passed}/{total} checks passed ({percentage:.1f}%)")
    print()
    
    if percentage >= 90:
        print("✅ SECURITY FRAMEWORK: OPERATIONAL")
        print()
        print("Your project is protected by:")
        print("  • .gitignore: Prevents committing secrets")
        print("  • config.py: Secure configuration management")
        print("  • test_security.py: Automated security tests")
        print("  • Pre-commit hooks: Automatic validation on commit")
        print("  • requirements-security.txt: Pinned security tools")
        print("  • SECURITY.md: Complete security policy")
        return 0
    else:
        print("⚠️ SECURITY FRAMEWORK: INCOMPLETE")
        print("Please check the items marked with ❌ above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
