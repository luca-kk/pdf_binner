# Domain.com.au Scraper

A command-line Python tool for sorting PDF files into X number of bins.

The original use case for this tool was to easily allocate multiple computers' OCR capabilities over a set of PDF files by dividing the files into subfolders.

---

## Features

- Targets all subfolders
- Moves PDF files into user inputted number of bins
- Algorithmically sorts files to keep final bin sizes similar
- Moves all non-PDF files into a Non-PDF folder

---

## Files Included

- `main.py` – Main script
- `README.md` – This file
- `pyproject.toml` – Poetry project configuration
- `poetry.lock` – Exact dependency versions
- `.gitignore` - Git ignore file

---

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

---

## Quick Start Guide

### 1. Clone or Download the Repository

*Option A: Using Git

```bash
git clone https://github.com/luca-kk/pdf_binner.git
cd pdf_binner
```

*Option B: Manual Download

- Download the Zip from GitHub repo
- Extract it
- Open a terminal inside the extracted folder

### 2. Install Dependencies with Poetry and Run

Located inside the downloaded repository, run:

```bash
poetry install --no-root
poetry run python pdf_binner.py
```
