#!/usr/bin/env python3
"""
Phase 4: Production Readiness - Security Assessment Tool

Comprehensive security scanning and vulnerability assessment for the multi-sensor
recording system, including both Python and Android components.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import socket
import ssl


@dataclass
class SecurityIssue:
    """Security issue finding"""
    severity: str  # critical, high, medium, low
    category: str
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: str = ""
    cve_id: Optional[str] = None


@dataclass
class SecurityReport:
    """Complete security assessment report"""
    timestamp: str
    scan_duration_seconds: float
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues: List[SecurityIssue]
    scanned_files: int
    recommendations: List[str]


class SecurityScanner:
    """Comprehensive security scanner for the project"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        self.issues: List[SecurityIssue] = []
        self.scanned_files = 0
        
    def _setup_logging(self) -> logging.Logger:
        """Setup security logging"""
        logger = logging.getLogger("SecurityScanner")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    async def run_comprehensive_scan(self) -> SecurityReport:
        """Run comprehensive security assessment"""
        start_time = datetime.now()
        
        self.logger.info("Starting comprehensive security assessment...")
        
        # Code analysis
        await self._scan_python_files()
        await self._scan_kotlin_java_files()
        await self._scan_configuration_files()
        
        # Network security
        await self._scan_network_security()
        
        # Dependency analysis
        await self._scan_dependencies()
        
        # File permissions and access
        await self._scan_file_permissions()
        
        # Secrets and credentials
        await self._scan_for_secrets()
        
        # Crypto and SSL analysis
        await self._scan_crypto_usage()
        
        # Android-specific security
        await self._scan_android_security()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate report
        report = self._generate_report(duration)
        self._save_report(report)
        
        return report
        
    async def _scan_python_files(self):
        """Scan Python files for security issues"""
        self.logger.info("Scanning Python files for security vulnerabilities...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if any(part.startswith('.') for part in py_file.parts):
                continue  # Skip hidden directories
                
            self.scanned_files += 1
            await self._analyze_python_file(py_file)
            
    async def _analyze_python_file(self, file_path: Path):
        """Analyze individual Python file for security issues"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for dangerous functions
                await self._check_dangerous_python_patterns(file_path, line_num, line)
                
                # Check for hardcoded credentials
                await self._check_hardcoded_secrets(file_path, line_num, line)
                
                # Check for SQL injection vulnerabilities
                await self._check_sql_injection(file_path, line_num, line)
                
                # Check for insecure random usage
                await self._check_insecure_random(file_path, line_num, line)
                
        except Exception as e:
            self.logger.warning(f"Error analyzing Python file {file_path}: {e}")
            
    async def _check_dangerous_python_patterns(self, file_path: Path, line_num: int, line: str):
        """Check for dangerous Python patterns"""
        dangerous_patterns = [
            (r'eval\s*\(', 'Use of eval() function'),
            (r'exec\s*\(', 'Use of exec() function'),
            (r'__import__\s*\(', 'Dynamic import usage'),
            (r'pickle\.loads?\s*\(', 'Insecure pickle usage'),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', 'Shell injection risk'),
            (r'os\.system\s*\(', 'Command injection risk'),
            (r'input\s*\(.*\)', 'Potential input validation issue'),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(SecurityIssue(
                    severity="high",
                    category="code_security",
                    title=description,
                    description=f"Potentially dangerous pattern found: {description}",
                    file_path=str(file_path),
                    line_number=line_num,
                    recommendation="Review usage and implement proper input validation/sanitization"
                ))
                
    async def _check_hardcoded_secrets(self, file_path: Path, line_num: int, line: str):
        """Check for hardcoded secrets and credentials"""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded token'),
            (r'["\'][A-Za-z0-9+/]{40,}={0,2}["\']', 'Potential base64 encoded secret'),
        ]
        
        for pattern, description in secret_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Skip obvious false positives
                if any(word in line.lower() for word in ['example', 'test', 'dummy', 'placeholder']):
                    continue
                    
                self.issues.append(SecurityIssue(
                    severity="critical",
                    category="credentials",
                    title=description,
                    description=f"Potential hardcoded credential found: {description}",
                    file_path=str(file_path),
                    line_number=line_num,
                    recommendation="Move secrets to environment variables or secure configuration"
                ))
                
    async def _check_sql_injection(self, file_path: Path, line_num: int, line: str):
        """Check for SQL injection vulnerabilities"""
        sql_patterns = [
            (r'execute\s*\([^)]*%[^)]*\)', 'String formatting in SQL'),
            (r'cursor\.execute\s*\([^)]*\+[^)]*\)', 'String concatenation in SQL'),
            (r'\.format\s*\([^)]*\).*execute', 'String format in SQL query'),
        ]
        
        for pattern, description in sql_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(SecurityIssue(
                    severity="high",
                    category="injection",
                    title="Potential SQL injection",
                    description=f"SQL injection vulnerability: {description}",
                    file_path=str(file_path),
                    line_number=line_num,
                    recommendation="Use parameterized queries or prepared statements"
                ))
                
    async def _check_insecure_random(self, file_path: Path, line_num: int, line: str):
        """Check for insecure random number generation"""
        if re.search(r'random\.random\(\)|random\.randint\(', line):
            if any(word in line.lower() for word in ['password', 'token', 'key', 'secret', 'nonce']):
                self.issues.append(SecurityIssue(
                    severity="medium",
                    category="cryptography",
                    title="Insecure random generation",
                    description="Using non-cryptographic random for security-sensitive operation",
                    file_path=str(file_path),
                    line_number=line_num,
                    recommendation="Use secrets module or os.urandom() for cryptographic purposes"
                ))
                
    async def _scan_kotlin_java_files(self):
        """Scan Kotlin/Java files for security issues"""
        self.logger.info("Scanning Kotlin/Java files for security vulnerabilities...")
        
        android_files = list(self.project_root.rglob("*.kt")) + list(self.project_root.rglob("*.java"))
        
        for file_path in android_files:
            if any(part.startswith('.') for part in file_path.parts):
                continue
                
            self.scanned_files += 1
            await self._analyze_android_file(file_path)
            
    async def _analyze_android_file(self, file_path: Path):
        """Analyze Android source files for security issues"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for dangerous Android patterns
                await self._check_dangerous_android_patterns(file_path, line_num, line)
                
                # Check for insecure storage
                await self._check_insecure_storage(file_path, line_num, line)
                
                # Check for network security issues
                await self._check_network_security_issues(file_path, line_num, line)
                
        except Exception as e:
            self.logger.warning(f"Error analyzing Android file {file_path}: {e}")
            
    async def _check_dangerous_android_patterns(self, file_path: Path, line_num: int, line: str):
        """Check for dangerous Android patterns"""
        dangerous_patterns = [
            (r'setJavaScriptEnabled\s*\(\s*true\s*\)', 'JavaScript enabled in WebView'),
            (r'addJavascriptInterface\s*\(', 'JavaScript interface in WebView'),
            (r'MODE_WORLD_READABLE|MODE_WORLD_WRITABLE', 'World-accessible file modes'),
            (r'checkCallingPermission\s*\(', 'Deprecated permission check'),
            (r'Runtime\.getRuntime\(\)\.exec\s*\(', 'Runtime.exec() usage'),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(SecurityIssue(
                    severity="high",
                    category="android_security",
                    title=description,
                    description=f"Dangerous Android pattern: {description}",
                    file_path=str(file_path),
                    line_number=line_num,
                    recommendation="Review and implement secure alternatives"
                ))
                
    async def _check_insecure_storage(self, file_path: Path, line_num: int, line: str):
        """Check for insecure storage patterns"""
        storage_patterns = [
            (r'SharedPreferences.*MODE_WORLD_READABLE', 'World-readable SharedPreferences'),
            (r'openFileOutput.*MODE_WORLD_READABLE', 'World-readable file output'),
            (r'getExternalStorageDirectory\(\)', 'External storage usage'),
        ]
        
        for pattern, description in storage_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(SecurityIssue(
                    severity="medium",
                    category="data_storage",
                    title="Insecure data storage",
                    description=f"Insecure storage pattern: {description}",
                    file_path=str(file_path),
                    line_number=line_num,
                    recommendation="Use private storage modes and encrypt sensitive data"
                ))
                
    async def _check_network_security_issues(self, file_path: Path, line_num: int, line: str):
        """Check for network security issues"""
        network_patterns = [
            (r'http://', 'Unencrypted HTTP usage'),
            (r'TrustAllX509TrustManager|NullHostnameVerifier', 'Disabled certificate validation'),
            (r'setHostnameVerifier.*ALLOW_ALL', 'Disabled hostname verification'),
        ]
        
        for pattern, description in network_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                severity = "critical" if "trust" in description.lower() else "medium"
                self.issues.append(SecurityIssue(
                    severity=severity,
                    category="network_security",
                    title="Network security issue",
                    description=f"Network security vulnerability: {description}",
                    file_path=str(file_path),
                    line_number=line_num,
                    recommendation="Use HTTPS and proper certificate validation"
                ))
                
    async def _scan_configuration_files(self):
        """Scan configuration files for security issues"""
        self.logger.info("Scanning configuration files...")
        
        config_files = (
            list(self.project_root.rglob("*.json")) +
            list(self.project_root.rglob("*.xml")) +
            list(self.project_root.rglob("*.yml")) +
            list(self.project_root.rglob("*.yaml")) +
            list(self.project_root.rglob("*.properties"))
        )
        
        for config_file in config_files:
            if any(part.startswith('.') for part in config_file.parts):
                continue
                
            self.scanned_files += 1
            await self._analyze_config_file(config_file)
            
    async def _analyze_config_file(self, file_path: Path):
        """Analyze configuration files for security issues"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check for credentials in config
            if re.search(r'password|secret|key.*[=:].*[^{]', content, re.IGNORECASE):
                self.issues.append(SecurityIssue(
                    severity="high",
                    category="configuration",
                    title="Potential credentials in config",
                    description="Configuration file may contain hardcoded credentials",
                    file_path=str(file_path),
                    recommendation="Use environment variables or secure configuration management"
                ))
                
            # Check for debug settings in production
            if file_path.name.endswith('.xml'):  # Android manifest
                if re.search(r'android:debuggable\s*=\s*["\']true["\']', content):
                    self.issues.append(SecurityIssue(
                        severity="medium",
                        category="configuration",
                        title="Debug mode enabled",
                        description="Application has debug mode enabled",
                        file_path=str(file_path),
                        recommendation="Disable debug mode in production builds"
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error analyzing config file {file_path}: {e}")
            
    async def _scan_network_security(self):
        """Scan network security configuration"""
        self.logger.info("Scanning network security configuration...")
        
        # Check protocol configuration
        config_file = self.project_root / "protocol" / "config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    
                # Check for insecure configurations
                if config.get("security", {}).get("encryption_enabled", False) is False:
                    self.issues.append(SecurityIssue(
                        severity="high",
                        category="network_security",
                        title="Encryption disabled",
                        description="Network encryption is disabled in configuration",
                        file_path=str(config_file),
                        recommendation="Enable encryption for network communications"
                    ))
                    
                if config.get("security", {}).get("authentication_required", False) is False:
                    self.issues.append(SecurityIssue(
                        severity="medium",
                        category="network_security",
                        title="Authentication disabled",
                        description="Network authentication is disabled",
                        file_path=str(config_file),
                        recommendation="Enable authentication for network connections"
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Error analyzing network config: {e}")
                
    async def _scan_dependencies(self):
        """Scan dependencies for known vulnerabilities"""
        self.logger.info("Scanning dependencies for vulnerabilities...")
        
        # Check Python dependencies
        requirements_files = list(self.project_root.rglob("requirements*.txt"))
        for req_file in requirements_files:
            await self._check_python_dependencies(req_file)
            
        # Check environment.yml
        env_file = self.project_root / "environment.yml"
        if env_file.exists():
            await self._check_conda_dependencies(env_file)
            
        # Check Gradle dependencies
        gradle_files = list(self.project_root.rglob("build.gradle"))
        for gradle_file in gradle_files:
            await self._check_gradle_dependencies(gradle_file)
            
    async def _check_python_dependencies(self, requirements_file: Path):
        """Check Python dependencies for vulnerabilities"""
        try:
            # This would typically use a vulnerability database
            # For now, I'll check for some known problematic packages
            content = requirements_file.read_text()
            
            vulnerable_packages = [
                "pycrypto",  # Deprecated, use pycryptodome
                "requests==2.25.1",  # Known CVE
            ]
            
            for vuln_pkg in vulnerable_packages:
                if vuln_pkg in content:
                    self.issues.append(SecurityIssue(
                        severity="high",
                        category="dependencies",
                        title="Vulnerable dependency",
                        description=f"Potentially vulnerable package: {vuln_pkg}",
                        file_path=str(requirements_file),
                        recommendation="Update to secure version or replace with alternative"
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error checking Python dependencies: {e}")
            
    async def _check_conda_dependencies(self, env_file: Path):
        """Check conda environment for vulnerabilities"""
        # Similar to Python dependencies but for conda packages
        pass
        
    async def _check_gradle_dependencies(self, gradle_file: Path):
        """Check Gradle dependencies for vulnerabilities"""
        try:
            content = gradle_file.read_text()
            
            # Check for vulnerable versions
            vulnerable_patterns = [
                (r'com\.google\.android\.material:material:1\.[0-6]\.', 'Outdated Material Design library'),
                (r'androidx\.core:core-ktx:1\.[0-5]\.', 'Outdated AndroidX Core library'),
            ]
            
            for pattern, description in vulnerable_patterns:
                if re.search(pattern, content):
                    self.issues.append(SecurityIssue(
                        severity="medium",
                        category="dependencies",
                        title="Outdated dependency",
                        description=f"Potentially outdated dependency: {description}",
                        file_path=str(gradle_file),
                        recommendation="Update to latest stable version"
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error checking Gradle dependencies: {e}")
            
    async def _scan_file_permissions(self):
        """Scan file permissions for security issues"""
        self.logger.info("Scanning file permissions...")
        
        # Check for overly permissive files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                try:
                    stat_info = file_path.stat()
                    mode = oct(stat_info.st_mode)[-3:]
                    
                    # Check for world-writable files
                    if mode.endswith('6') or mode.endswith('7'):
                        self.issues.append(SecurityIssue(
                            severity="medium",
                            category="file_permissions",
                            title="Overly permissive file permissions",
                            description=f"File has world-writable permissions: {mode}",
                            file_path=str(file_path),
                            recommendation="Restrict file permissions to necessary access only"
                        ))
                        
                except Exception:
                    pass  # Permission denied or other errors
                    
    async def _scan_for_secrets(self):
        """Scan for exposed secrets and API keys"""
        self.logger.info("Scanning for exposed secrets...")
        
        # Patterns for various types of secrets
        secret_patterns = [
            (r'sk_live_[0-9a-zA-Z]{24}', 'Stripe live secret key'),
            (r'sk_test_[0-9a-zA-Z]{24}', 'Stripe test secret key'),
            (r'AKIA[0-9A-Z]{16}', 'AWS access key'),
            (r'AIza[0-9A-Za-z\-_]{35}', 'Google API key'),
            (r'[0-9a-fA-F]{32}', 'Potential MD5 hash'),
            (r'github_pat_[0-9a-zA-Z_]{82}', 'GitHub personal access token'),
        ]
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.kt', '.java', '.js', '.json', '.yml', '.yaml']:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    for pattern, description in secret_patterns:
                        if re.search(pattern, content):
                            self.issues.append(SecurityIssue(
                                severity="critical",
                                category="secrets",
                                title="Exposed secret",
                                description=f"Potential exposed secret: {description}",
                                file_path=str(file_path),
                                recommendation="Remove secret from code and use secure storage"
                            ))
                            
                except Exception:
                    pass
                    
    async def _scan_crypto_usage(self):
        """Scan cryptographic usage for security issues"""
        self.logger.info("Scanning cryptographic implementations...")
        
        crypto_patterns = [
            (r'MD5|md5', 'Weak hash algorithm MD5'),
            (r'SHA1|sha1', 'Weak hash algorithm SHA1'),
            (r'DES|des', 'Weak encryption algorithm DES'),
            (r'RC4|rc4', 'Weak encryption algorithm RC4'),
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for pattern, description in crypto_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.issues.append(SecurityIssue(
                            severity="medium",
                            category="cryptography",
                            title="Weak cryptographic algorithm",
                            description=f"Usage of weak algorithm: {description}",
                            file_path=str(file_path),
                            recommendation="Use strong cryptographic algorithms (AES, SHA-256, etc.)"
                        ))
                        
            except Exception:
                pass
                
    async def _scan_android_security(self):
        """Scan Android-specific security configurations"""
        self.logger.info("Scanning Android security configurations...")
        
        # Check AndroidManifest.xml
        manifest_path = self.project_root / "AndroidApp" / "src" / "main" / "AndroidManifest.xml"
        if manifest_path.exists():
            await self._analyze_android_manifest(manifest_path)
            
        # Check ProGuard configuration
        proguard_files = list(self.project_root.rglob("proguard-rules.pro"))
        for proguard_file in proguard_files:
            await self._analyze_proguard_config(proguard_file)
            
    async def _analyze_android_manifest(self, manifest_path: Path):
        """Analyze Android manifest for security issues"""
        try:
            content = manifest_path.read_text()
            
            security_checks = [
                (r'android:exported\s*=\s*["\']true["\']', 'Exported component'),
                (r'android:allowBackup\s*=\s*["\']true["\']', 'Backup allowed'),
                (r'android:usesCleartextTraffic\s*=\s*["\']true["\']', 'Cleartext traffic allowed'),
                (r'android:debuggable\s*=\s*["\']true["\']', 'Debug mode enabled'),
            ]
            
            for pattern, description in security_checks:
                if re.search(pattern, content):
                    severity = "high" if "debug" in description.lower() else "medium"
                    self.issues.append(SecurityIssue(
                        severity=severity,
                        category="android_manifest",
                        title=f"Android manifest issue: {description}",
                        description=f"Potentially insecure manifest setting: {description}",
                        file_path=str(manifest_path),
                        recommendation="Review and secure manifest configuration"
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error analyzing Android manifest: {e}")
            
    async def _analyze_proguard_config(self, proguard_path: Path):
        """Analyze ProGuard configuration"""
        try:
            content = proguard_path.read_text()
            
            # Check for disabled obfuscation
            if re.search(r'-dontobfuscate', content):
                self.issues.append(SecurityIssue(
                    severity="medium",
                    category="code_protection",
                    title="Obfuscation disabled",
                    description="Code obfuscation is disabled in ProGuard",
                    file_path=str(proguard_path),
                    recommendation="Enable obfuscation for production builds"
                ))
                
        except Exception as e:
            self.logger.warning(f"Error analyzing ProGuard config: {e}")
            
    def _generate_report(self, duration: float) -> SecurityReport:
        """Generate comprehensive security report"""
        
        # Count issues by severity
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        high_count = len([i for i in self.issues if i.severity == "high"])
        medium_count = len([i for i in self.issues if i.severity == "medium"])
        low_count = len([i for i in self.issues if i.severity == "low"])
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations()
        
        return SecurityReport(
            timestamp=datetime.now().isoformat(),
            scan_duration_seconds=duration,
            total_issues=len(self.issues),
            critical_issues=critical_count,
            high_issues=high_count,
            medium_issues=medium_count,
            low_issues=low_count,
            issues=self.issues,
            scanned_files=self.scanned_files,
            recommendations=recommendations
        )
        
    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        if any(i.category == "credentials" for i in self.issues):
            recommendations.append(
                "Implement secure credential management using environment variables or secret management systems"
            )
            
        if any(i.category == "network_security" for i in self.issues):
            recommendations.append(
                "Enable HTTPS/TLS encryption for all network communications and implement certificate pinning"
            )
            
        if any(i.category == "dependencies" for i in self.issues):
            recommendations.append(
                "Regularly update dependencies and implement automated vulnerability scanning in CI/CD"
            )
            
        if any(i.category == "android_security" for i in self.issues):
            recommendations.append(
                "Review Android security configuration including manifest permissions and ProGuard settings"
            )
            
        if any(i.category == "cryptography" for i in self.issues):
            recommendations.append(
                "Use modern cryptographic algorithms and implement proper key management"
            )
            
        if not self.issues:
            recommendations.append("No major security issues detected. Continue following security best practices.")
            
        return recommendations
        
    def _save_report(self, report: SecurityReport):
        """Save security report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.project_root / "security_reports"
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        json_file = output_dir / f"security_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
            
        # Save human-readable report
        txt_file = output_dir / f"security_summary_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write("=== Security Assessment Report ===\n\n")
            f.write(f"Scan completed: {report.timestamp}\n")
            f.write(f"Duration: {report.scan_duration_seconds:.2f} seconds\n")
            f.write(f"Files scanned: {report.scanned_files}\n\n")
            
            f.write("=== Issue Summary ===\n")
            f.write(f"Total issues: {report.total_issues}\n")
            f.write(f"Critical: {report.critical_issues}\n")
            f.write(f"High: {report.high_issues}\n")
            f.write(f"Medium: {report.medium_issues}\n")
            f.write(f"Low: {report.low_issues}\n\n")
            
            if report.issues:
                f.write("=== Detailed Issues ===\n")
                for issue in sorted(report.issues, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x.severity]):
                    f.write(f"\n[{issue.severity.upper()}] {issue.title}\n")
                    f.write(f"Category: {issue.category}\n")
                    f.write(f"Description: {issue.description}\n")
                    if issue.file_path:
                        f.write(f"File: {issue.file_path}")
                        if issue.line_number:
                            f.write(f":{issue.line_number}")
                        f.write("\n")
                    if issue.recommendation:
                        f.write(f"Recommendation: {issue.recommendation}\n")
                    f.write("-" * 50 + "\n")
                    
            f.write("\n=== Recommendations ===\n")
            for i, rec in enumerate(report.recommendations, 1):
                f.write(f"{i}. {rec}\n")
                
        self.logger.info(f"Security report saved to {json_file}")
        self.logger.info(f"Security summary saved to {txt_file}")


async def main():
    """Run security assessment"""
    project_root = Path(__file__).parent.parent.parent
    
    print("Starting Phase 4 Security Assessment...")
    
    scanner = SecurityScanner(str(project_root))
    
    try:
        report = await scanner.run_comprehensive_scan()
        
        print(f"\nSecurity scan completed!")
        print(f"Files scanned: {report.scanned_files}")
        print(f"Total issues found: {report.total_issues}")
        print(f"  Critical: {report.critical_issues}")
        print(f"  High: {report.high_issues}")
        print(f"  Medium: {report.medium_issues}")
        print(f"  Low: {report.low_issues}")
        
        if report.critical_issues > 0:
            print("\n⚠️  CRITICAL ISSUES FOUND - Immediate action required!")
            
        print(f"\nTop recommendations:")
        for i, rec in enumerate(report.recommendations[:3], 1):
            print(f"  {i}. {rec}")
            
        print(f"\nDetailed reports saved to: {project_root}/security_reports/")
        
    except Exception as e:
        print(f"Security scan failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())