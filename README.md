# pdf2john
[![Tests](https://github.com/benjamin-awd/pdf2john/workflows/tests/badge.svg)](https://github.com/pdf2john-awd/monopoly/actions)
[![CI](https://github.com/benjamin-awd/pdf2john/workflows/ci/badge.svg)](https://github.com/pdf2john/monopoly/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-orange)](https://github.com/pylint-dev/pylint)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern refactoring of the legacy pdf2john.py library, aimed at making the code easier to read and maintain.

## Install
Install dependencies using [Homebrew](https://brew.sh/)
```bash
brew bundle
```

Create a virtual environment and install Python dependencies
```bash
pyenv virtualenv 3.11.4 pdf2john
pyenv shell pdf2john
poetry install --only main
```

## Usage
To pass the hash to john:
```bash
pdf2john example.pdf >> .hash
john .hash
john --show --format=PDF .hash
```

If you don't want to use poetry, you can run pdf2john as a standalone script:
```bash
git clone https://github.com/benjamin-awd/pdf2john.git
cd pdf2john && pip install -r requirements.txt
./src/pdf2john/pdf2john.py example.pdf >> .hash
```

## Features
- Responsibility for PDF parsing and handling has been delegated to [pyHanko](https://github.com/MatthiasValvekens/pyHanko) (a crytography focused fork of PyPDF2)
- CICD workflow that tests pdf2john against PDFs ranging from Security Handler Revision 2 -> 6
- Removal of legacy Python 2.x support
- An optional debugging flag that shows the encryption dictionary of a PDF
- Readability improvements (a general attempt to be more Pythonic)

## Troubleshooting
To access the encryption dictionary:
```bash
./pdf2john.py tests/pdf/pypdf/r6-user-password.pdf --debug
```

## Acknowledgement
This repository was based on the original pdf2john.py by [Shane Quigley](https://github.com/ShaneQful)
