## Overview
PyQtChess is a desktop application which provides a Chess GUI written in PyQt5, along with an integrated chess engine written in pure Python. Unlike most other pure Python chess engines, PyQtChess is focused on playing strength, and has an Elo rating of ~2150.

## Supported Platforms
* Linux (All Python versions)
* Windows 64-bit (Python versions 3.4 - 3.9)

## Installation

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install wheel
pip install -r requirements.txt
```

### Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install wheel
pip install -r requirements.txt
```

After installation the program can be executed with `python main.py`.