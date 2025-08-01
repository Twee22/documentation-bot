#!/usr/bin/env python3
"""
Setup script for the Documentation Bot package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="documentation-bot",
    version="1.0.0",
    author="Documentation Bot Team",
    author_email="your-email@example.com",
    description="An agentic system for generating comprehensive documentation for code repositories",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/documentation-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "documentation-bot=documentation_bot:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="documentation, openai, llm, code-analysis, markdown",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/documentation-bot/issues",
        "Source": "https://github.com/yourusername/documentation-bot",
        "Documentation": "https://github.com/yourusername/documentation-bot#readme",
    },
) 