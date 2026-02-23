#!/usr/bin/env python3
"""
Hyvor Relay Email Skill - 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取 README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# 读取 requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="hyvor-relay-email",
    version="1.0.0",
    author="TomiBot",
    author_email="tomibot@163.com",
    description="Hyvor Relay 邮件服务 Python 客户端和 Skill",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyvor/relay",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "hyvor_relay": ["py.typed"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "web": [
            "flask>=2.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "grafana-dashboard>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hyvor-relay-configure=scripts.configure:main",
            "hyvor-relay-test=scripts.test_email:main",
            "hyvor-relay-monitor=scripts.monitor:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords="email, hyvor, relay, smtp, api, self-hosted",
    project_urls={
        "Documentation": "https://relay.hyvor.com/docs",
        "Source": "https://github.com/hyvor/relay",
        "Tracker": "https://github.com/hyvor/relay/issues",
    },
)