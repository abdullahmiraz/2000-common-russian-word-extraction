#!/usr/bin/env python3
"""
LaTeX Book Generator for 2000 Most Common Russian Words in Context
Converts entries.json into modular LaTeX chapters and master document (A4 Two-Column format).
"""

import os
import re
import json
from typing import List, Dict, Any


def format_phonetics(text: str) -> str:
    """Wrap phonetic/IPA characters or bracketed transcriptions with ipafont."""
    if not text:
        return ""
    # Wrap square bracketed phonetic substrings in meanings with ipafont
    text = re.sub(r'(\[[^\]]+\])', r'{\\ipafont \1}', text)
    # Also wrap standalone phonetic vowels like ə and ɛ
    text = text.replace("ə", r"{\ipafont ə}")
    text = text.replace("ɛ", r"{\ipafont ɛ}")
    return text


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters while preserving UTF-8 typography."""
    if not text:
        return ""
    text = text.replace("\\", r"\textbackslash{}")
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("$", r"\$")
    text = text.replace("#", r"\#")
    text = text.replace("_", r"\_")
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("~", r"\textasciitilde{}")
    text = text.replace("^", r"\textasciicircum{}")
    return text


def clean_source_typos(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Correct known typos and homoglyphs from the original PDF."""
    e = dict(entry)
    num = e["number"]

    # Entry 87: 'Co' (Latin C, o) -> 'Со' (Cyrillic С, о)
    if num == 87:
        e["russian_word"] = "Со"

    # Entry 197: English example contains Cyrillic 'а' in 'а divorce'
    if num == 197:
        e["english_example"] = e["english_example"].replace("\u0430 divorce", "a divorce")

    # Entry 366: Unbalanced bracket in source 'nouns])'
    if num == 366:
        e["english_meaning"] = e["english_meaning"].replace("nouns])", "nouns)")

    # Entry 959: 'Cтавить' (Latin C) -> 'Ставить' (Cyrillic С)
    if num == 959:
        e["russian_word"] = "Ставить"

    # Entry 1825: 'cвоего' (Latin c) -> 'своего' (Cyrillic с)
    if num == 1825:
        e["russian_example"] = e["russian_example"].replace("cвоего", "своего")

    return e


CHAPTER_TITLES = [
    (1, 250, "The Core Essentials", "The most fundamental building blocks of Russian: pronouns, prepositions, and primary everyday verbs."),
    (251, 500, "Everyday Communication", "Essential vocabulary for daily activities, family, time, places, and common conversational expressions."),
    (501, 750, "Expanding Expression", "Verbs of action, descriptive adjectives, basic concepts, and common social vocabulary."),
    (751, 1000, "Intermediate Milestone", "Key transition vocabulary reaching the 1,000-word milestone for conversational fluency."),
    (1001, 1250, "Nuanced Concepts", "Abstract ideas, emotions, professional contexts, and multifaceted verbs."),
    (1251, 1500, "Complex Descriptions", "Descriptive adjectives, compound expressions, specialized terminology, and literary phrasing."),
    (1501, 1750, "Professional and Literary Vocabulary", "Higher-register verbs, formal dialogue, culture, science, and societal terminology."),
    (1751, 2000, "Advanced Mastery", "Final frequency tier reaching full 2,000-word mastery for advanced reading and comprehension."),
]


def generate_chapters(entries: List[Dict[str, Any]], chapters_dir: str):
    """Generate chapter .tex files with 2-column layout."""
    os.makedirs(chapters_dir, exist_ok=True)
    
    for ch_idx, (start_num, end_num, title, subtitle) in enumerate(CHAPTER_TITLES, start=1):
        ch_entries = [e for e in entries if start_num <= e["number"] <= end_num]
        ch_file = os.path.join(chapters_dir, f"chapter{ch_idx}.tex")
        
        with open(ch_file, "w", encoding="utf-8") as f:
            f.write(f"% Chapter {ch_idx}: Words {start_num} - {end_num}\n")
            f.write(f"\\chapter{{{title}}}\n")
            f.write(f"\\label{{chap:chapter{ch_idx}}}\n\n")
            f.write(f"{{\\small\\sffamily\\color{{mutedtext}} {subtitle}\\par}}\n\n")
            f.write(f"\\vspace{{0.4em}}\n")
            f.write(f"\\markboth{{Chapter {ch_idx}: {title}}}{{Words {start_num}--{end_num}}}\n\n")
            f.write(f"\\begin{{multicols}}{{2}}\n")

            for e in ch_entries:
                num = e["number"]
                word = escape_latex(e["russian_word"])
                pron = escape_latex(e["pronunciation"])
                meaning = format_phonetics(escape_latex(e["english_meaning"]))
                ru_ex = escape_latex(e["russian_example"])
                en_ex = escape_latex(e["english_example"])

                f.write(f"\\vocentry{{{num}}}{{{word}}}{{{pron}}}{{{meaning}}}{{{ru_ex}}}{{{en_ex}}}\n")

            f.write(f"\\end{{multicols}}\n")

    print(f"Generated {len(CHAPTER_TITLES)} chapters in '{chapters_dir}'.")


def generate_index(entries: List[Dict[str, Any]], backmatter_dir: str):
    """Generate Alphabetical Russian Index in backmatter (4-column A4 format)."""
    os.makedirs(backmatter_dir, exist_ok=True)
    index_file = os.path.join(backmatter_dir, "index.tex")

    sorted_entries = sorted(entries, key=lambda x: x["russian_word"].lower())

    with open(index_file, "w", encoding="utf-8") as f:
        f.write("\\chapter*{Alphabetical Word Index}\n")
        f.write("\\addcontentsline{toc}{chapter}{Alphabetical Word Index}\n")
        f.write("\\markboth{Alphabetical Word Index}{Alphabetical Word Index}\n\n")
        f.write("{\\small\\color{mutedtext} Quick alphabetical index of all 2000 Russian headwords with frequency rankings.}\\par\n\n")
        f.write("\\vspace{0.8em}\n")
        f.write("\\begin{multicols}{4}\n")
        f.write("\\raggedright\\footnotesize\n")

        current_letter = ""
        for e in sorted_entries:
            word = e["russian_word"]
            first_char = word[0].upper()
            if first_char != current_letter:
                current_letter = first_char
                f.write(f"\n\\vspace{{0.6em}}\\noindent\\textbf{{\\normalsize\\sffamily\\color{{primary}} {current_letter}}}\\par\\vspace{{0.2em}}\n")
            
            esc_word = escape_latex(word)
            num = e["number"]
            f.write(f"\\noindent {esc_word} \\dotfill \\textbf{{\\color{{secondary}} {num}}}\\par\n")

        f.write("\\end{multicols}\n")
    print(f"Generated Alphabetical Index in '{index_file}'.")


def generate_main_tex(latex_dir: str):
    """Generate main.tex master document."""
    main_path = os.path.join(latex_dir, "main.tex")
    
    chapter_includes = "\n".join([f"  \\input{{chapters/chapter{i}}}" for i in range(1, 9)])

    content = f"""\\documentclass[10pt,twoside,openright]{{extbook}}

\\input{{preamble.tex}}

\\begin{{document}}

% Front Matter
\\frontmatter
\\input{{frontmatter/titlepage}}
\\tableofcontents
\\input{{frontmatter/intro}}
\\input{{frontmatter/pronunciation}}

% Main Body
\\mainmatter
{chapter_includes}

% Back Matter
\\backmatter
\\input{{backmatter/index}}

\\end{{document}}
"""
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated master LaTeX file: '{main_path}'.")


def main():
    latex_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(latex_dir, "../data/entries.json")
    if not os.path.exists(data_file):
        data_file = os.path.join(latex_dir, "data/entries.json")

    print(f"Reading dataset: {data_file}")
    with open(data_file, "r", encoding="utf-8") as f:
        entries = json.load(f)

    cleaned_entries = [clean_source_typos(e) for e in entries]

    chapters_dir = os.path.join(latex_dir, "chapters")
    backmatter_dir = os.path.join(latex_dir, "backmatter")

    generate_chapters(cleaned_entries, chapters_dir)
    generate_index(cleaned_entries, backmatter_dir)
    generate_main_tex(latex_dir)
    print("LaTeX generation complete!")


if __name__ == "__main__":
    main()
