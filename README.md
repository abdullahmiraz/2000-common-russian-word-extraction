# 2000 Most Common Russian Words in Context

A complete, production-ready Python and LaTeX suite to extract, validate, and typeset all **2000 Russian vocabulary entries** from the book *"2000 Most Common Russian Words in Context"*.

---

## Highlights

- **Complete Dataset**: All 2000 vocabulary entries extracted with 100% accuracy using native PyMuPDF vector text extraction (0 missing, 0 duplicates).
- **Publication-Ready LaTeX Book (97 pages A4)**:
  - Redesigned into a modern, dense, highly readable **A4 2-Column layout** (reduced from the original 408 pages down to **97 pages**).
  - High-quality Russian typography using **PT Serif**, **PT Sans**, and **Charis SIL** for phonetic IPA transcriptions.
  - Organized into **8 frequency milestone chapters** (250 words per chapter).
  - Includes Front Matter (Title Page, Methodology, Pronunciation & Grammar guide) and Back Matter (**4-column Alphabetical Russian Word Index**).
  - Corrected all source PDF homoglyphs and typographical errors.

---

## Directory Structure

```
2000-common-russian-word-extraction/
├── data/
│   ├── entries.json                    # Complete 2000 entries structured JSON
│   ├── raw.txt                         # Raw text extracted from all 408 PDF pages
│   └── review_report.json              # Audit of source typos & homoglyphs
├── latex/                              # All LaTeX-related files
│   ├── 2000_Most_Common_Russian_Words.pdf  # Compiled 97-page publication book
│   ├── build_latex.py                  # Generates modular .tex files from JSON
│   ├── Makefile                        # One-command build automation
│   ├── main.tex                        # Master document (XeLaTeX)
│   ├── preamble.tex                    # Typography, fonts, colors, & layout
│   ├── frontmatter/                    # Titlepage, intro, pronunciation guide
│   ├── chapters/                       # 8 milestone chapter files
│   └── backmatter/                     # Alphabetical Russian index
├── extract.py                          # Native PyMuPDF extractor script
├── validate.py                         # Dataset integrity and schema validator
├── pyproject.toml                      # Standard project metadata & tech stack
├── requirements.txt                    # Minimal dependencies
└── README.md                           # Documentation
```

---

## Quick Start

### 1. Environment Setup

```bash
cd /home/neo/Documents/2000-common-russian-word-extraction

# Activate virtual environment
source .venv/bin/activate

# Or install dependencies
pip install -r requirements.txt
```

### 2. Extract & Validate Dataset

```bash
# Run extraction
python3 extract.py

# Run validation
python3 validate.py
```

### 3. Build LaTeX Book

All LaTeX files and scripts reside in the `latex/` directory:

```bash
cd latex

# Generate .tex sources from JSON and compile to PDF
python3 build_latex.py
xelatex -interaction=nonstopmode -output-directory=build main.tex
xelatex -interaction=nonstopmode -output-directory=build main.tex
cp build/main.pdf 2000_Most_Common_Russian_Words.pdf

# Or simply use make:
make pdf
```

---

## Dataset Schema (`data/entries.json`)

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

## Source Text Audit (`data/review_report.json`)

The following 5 quirks / typos in the original printed book were detected and cataloged (and corrected in the LaTeX edition):

1. **#87 (`Co`)**: Headword was typed with Latin `'C'` and `'o'` $\to$ fixed to Cyrillic `'С'` and `'о'`.
2. **#197 (`Про`)**: English example contained Cyrillic `'а'` in `"а divorce."` $\to$ fixed to Latin `'a'`.
3. **#366 (`Оба`)**: Extra closing bracket in source English meaning: `"Both (for masculine nouns])"` $\to$ fixed to `"Both (for masculine nouns)"`.
4. **#959 (`Cтавить`)**: Leading character was typed with Latin `'C'` $\to$ fixed to Cyrillic `'С'`.
5. **#1825 (`Сомневаться`)**: Russian example had Latin `'c'` in `"cвоего"` $\to$ fixed to Cyrillic `'с'`.
