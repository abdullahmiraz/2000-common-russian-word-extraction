# 2000 Most Common Russian Words Extractor

A robust, production-ready Python tool to extract, structure, and validate all **2000 Russian vocabulary entries** from the book *"2000 Most Common Russian Words in Context"*.

This dataset is cleanly parsed and formatted for downstream applications, including a future LaTeX book redesign.

---

## Technology Stack

The project uses a lightweight, high-performance Python stack:

* **Language**: [Python 3.10+](https://www.python.org/) (tested on Python 3.12)
* **PDF Parser Engine**: [PyMuPDF (`pymupdf` v1.28.2)](https://github.com/pymupdf/pymupdf)
  * Utilizes high-performance C/C++ bindings (MuPDF) for native vector text & font span extraction (`page.get_text("dict")`).
  * Extracts text styles, fonts (e.g. `Arial-BoldMT`, `Arial-BoldItalicMT`, `ArialMT`), and font flags to distinguish headwords, definitions, and sentence boundaries.
* **CLI & Utilities**:
  * `tqdm` (v4.70.1): Progress tracking during extraction.
  * `argparse`: Command-line interface argument parsing.
  * Standard library modules: `json`, `re`, `os`, `sys`, `typing`.
* **Configuration & Packaging**:
  * [`pyproject.toml`](./pyproject.toml): Standard PEP 621 project metadata and dependencies.
  * [`requirements.txt`](./requirements.txt): Minimal package requirements.
  * [`requirements-lock.txt`](./requirements-lock.txt): Exact pinned versions for reproducibility.
  * [`.venv/`](./.venv): Isolated virtual environment.

---

## Directory Structure

```
2000-common-russian-word-extraction/
├── data/
│   ├── entries.json          # Complete 2000 entries structured JSON
│   ├── raw.txt               # Raw text extracted from all 408 PDF pages
│   └── review_report.json    # Audit of source typos & homoglyphs
├── latex/                    # Reserved for LaTeX redesign template and builds
├── extract.py                # Native PyMuPDF extractor script
├── validate.py               # Dataset integrity and schema validator
├── pyproject.toml            # Project metadata & tech stack specification
├── requirements.txt          # Python dependencies
├── requirements-lock.txt     # Exact pinned dependency versions
└── README.md                 # Project documentation
```

---

## Dataset Schema (`data/entries.json`)

Every entry contains all 6 required fields:

```json
[
  {
    "number": 1,
    "russian_word": "И",
    "pronunciation": "i",
    "english_meaning": "And",
    "russian_example": "Вчера она купила фрукты и овощи.",
    "english_example": "She bought some fruit and vegetables yesterday."
  },
  {
    "number": 2,
    "russian_word": "В",
    "pronunciation": "v",
    "english_meaning": "In, on, at",
    "russian_example": "Маленький котёнок спрятался в подвале.",
    "english_example": "A little kitten hid in the basement."
  }
]
```

---

## Quick Start

### 1. Environment Setup

```bash
cd /home/neo/Documents/2000-common-russian-word-extraction

# Activate virtual environment
source .venv/bin/activate

# Or install dependencies in a new environment
pip install -r requirements.txt
```

### 2. Run Extraction

```bash
python3 extract.py
```
*Optional parameters:*
* `--pdf <path>`: Custom PDF path (defaults to `/home/neo/Documents/2000_Most_Common_Russian_Words_in_Context_Get_Fluent_Increase_Your.pdf`)
* `--output <path>`: Custom JSON output path (defaults to `data/entries.json`)
* `--raw-output <path>`: Custom raw text output path (defaults to `data/raw.txt`)
* `--report <path>`: Custom audit report path (defaults to `data/review_report.json`)

### 3. Run Validation

```bash
python3 validate.py
```
*Optional parameters:*
* `--file <path>`: Path to JSON file (defaults to `data/entries.json`)

---

## Validation & Quality Assurance

The dataset has passed automated validation:
- **Completeness**: Exactly 2000 entries (IDs `1` through `2000`).
- **Uniqueness**: 0 missing IDs, 0 duplicate IDs.
- **Integrity**: 0 empty fields across all 2000 records.
- **Multilingual Separation**: Russian headwords and sentences contain valid Cyrillic characters; English examples contain valid Latin characters.

### Source Text Audit (`data/review_report.json`)

The following 5 quirks / typos in the original printed book were detected and cataloged:

1. **#87 (`Co`)**: Headword was typed with Latin `'C'` and `'o'` instead of Cyrillic `'С'` and `'о'`.
2. **#197 (`Про`)**: English example contains Cyrillic `'а'` in `"а divorce."` instead of Latin `'a'`.
3. **#366 (`Оба`)**: Extra closing bracket in source English meaning: `"Both (for masculine nouns])"`.
4. **#959 (`Cтавить`)**: Leading character was typed with Latin `'C'` instead of Cyrillic `'С'`.
5. **#1825 (`Сомневаться`)**: Russian example has Latin `'c'` in `"cвоего"` instead of Cyrillic `'с'`.
