"""
Setup configuration for CodeArchitect AI
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="code-architect-ai",
    version="1.0.0",
    author="CodeArchitect AI",
    description="Transform your React Native codebase into an intelligent knowledge base",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/code-architect-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "openai>=1.12.0",
        "tiktoken>=0.5.2",
        "tenacity>=8.2.3",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "black>=24.1.1",
            "flake8>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cortex=main:main",
        ],
    },
)

