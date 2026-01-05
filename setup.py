"""Setup configuration for git-tag-lookup."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from __init__.py
version = "0.1.0"
init_file = Path(__file__).parent / "git_tag_lookup" / "__init__.py"
if init_file.exists():
    for line in init_file.read_text(encoding="utf-8").split("\n"):
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read requirements
requirements = []
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").split("\n")
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="git-tag-lookup",
    version=version,
    description="A tool to lookup git tags and search commits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="https://github.com/yourusername/git-tag-lookup",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "git-tag-lookup=git_tag_lookup.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)

