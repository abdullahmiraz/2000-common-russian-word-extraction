#!/usr/bin/env python3
"""
Extractor for 2000 Most Common Russian Words in Context
Extracts vocabulary entries from PDF using PyMuPDF (pymupdf) into structured JSON.
"""

import os
import re
import json
import argparse
from typing import List, Dict, Any, Tuple
import pymupdf


def extract_raw_text(doc: pymupdf.Document, raw_output_path: str) -> str:
    """Extract raw text from all pages of the document and save to file."""
    os.makedirs(os.path.dirname(os.path.abspath(raw_output_path)), exist_ok=True)
    raw_pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        raw_pages.append(f"--- PAGE {page_num + 1} ---\n{text}")
    
    full_raw_text = "\n".join(raw_pages)
    with open(raw_output_path, "w", encoding="utf-8") as f:
        f.write(full_raw_text)
    return full_raw_text


def join_text_lines(lines: List[str]) -> str:
    """Join multiple lines handling hyphenated words properly."""
    if not lines:
        return ""
    res = lines[0]
    for nxt in lines[1:]:
        if res.endswith("-") and not res.endswith(" -"):
            res = res + nxt
        else:
            res = res + " " + nxt
    return re.sub(r"\s+", " ", res).strip()


def count_chars(text: str) -> Tuple[int, int]:
    """Count Cyrillic and Latin characters in a string."""
    cyr = sum(1 for c in text if "\u0400" <= c <= "\u04ff" or "\u0500" <= c <= "\u052f")
    lat = sum(1 for c in text if "a" <= c.lower() <= "z")
    return cyr, lat


def extract_entries(doc: pymupdf.Document, start_page: int = 12, end_page: int = 404) -> List[Dict[str, Any]]:
    """
    Extract vocabulary entries 1-2000 from the PDF document.
    start_page and end_page are 1-based page numbers.
    """
    lines_meta = []
    
    # 0-indexed page range
    for pno in range(start_page - 1, end_page):
        page = doc[pno]
        d = page.get_text("dict")
        for b in d.get("blocks", []):
            if "lines" in b:
                for l in b["lines"]:
                    line_text = "".join([s["text"] for s in l.get("spans", [])]).strip()
                    if not line_text:
                        continue
                    # Skip top title header on the first vocabulary page
                    if pno == start_page - 1 and line_text in [
                        "2000 Most Common Russian",
                        "Words In Context",
                    ]:
                        continue
                    
                    fonts = [s.get("font", "") for s in l.get("spans", [])]
                    is_all_bi = all("BoldItalic" in f or "Italic" in f for f in fonts)
                    has_regular = any(f == "ArialMT" for f in fonts)
                    
                    lines_meta.append({
                        "page": pno + 1,
                        "text": line_text,
                        "fonts": fonts,
                        "is_all_bi": is_all_bi,
                        "has_regular": has_regular,
                    })

    # Header regexes
    entry_header_regex = re.compile(r"^(\d+)\s*(?:[-–—]\s*)?(.*)$")
    header_parser = re.compile(r"^(.*?)\s*\[(.*?)\]\s*(?:[-–—:]\s*)?(.*)$")

    entry_slices = []
    current_num = 1
    for idx, item in enumerate(lines_meta):
        m = entry_header_regex.match(item["text"])
        if m and int(m.group(1)) == current_num:
            entry_slices.append((current_num, idx))
            current_num += 1

    if len(entry_slices) != 2000:
        raise ValueError(f"Expected 2000 entries, but found {len(entry_slices)}")

    entries = []
    for i in range(len(entry_slices)):
        num, start_idx = entry_slices[i]
        end_idx = entry_slices[i + 1][1] if i + 1 < len(entry_slices) else len(lines_meta)
        entry_lines = lines_meta[start_idx:end_idx]

        header_line_0 = entry_lines[0]["text"]
        m = entry_header_regex.match(header_line_0)
        rest = m.group(2)
        hm = header_parser.match(rest)
        if not hm:
            raise ValueError(f"Could not parse header for entry {num}: {header_line_0}")

        word = hm.group(1).strip()
        pron = hm.group(2).strip()
        meaning_parts = [hm.group(3).strip()] if hm.group(3).strip() else []

        remaining_lines = entry_lines[1:]
        state = "meaning_cont"
        ru_lines = []
        en_lines = []

        for rline in remaining_lines:
            txt = rline["text"]
            cyr, lat = count_chars(txt)

            if state == "meaning_cont":
                # Meaning lines are BoldItalic or English explanatory notes in headers
                if rline["is_all_bi"] or (lat > cyr and not rline["has_regular"]):
                    meaning_parts.append(txt)
                elif (
                    not rline["has_regular"]
                    and (")" in txt or "’" in txt or "]" in txt)
                    and any(
                        kw in txt
                        for kw in [
                            "form", "noun", "verb", "used", "case",
                            "pronoun", "singular", "plural", "impersonal",
                            "perfective", "colloquial", "archaic"
                        ]
                    )
                ):
                    meaning_parts.append(txt)
                else:
                    state = "ru_sentence"
                    ru_lines.append(txt)
            elif state == "ru_sentence":
                # Transition to English example when predominant alphabet is Latin
                if lat > cyr:
                    state = "en_sentence"
                    en_lines.append(txt)
                else:
                    ru_lines.append(txt)
            elif state == "en_sentence":
                en_lines.append(txt)

        entries.append({
            "number": num,
            "russian_word": word,
            "pronunciation": pron,
            "english_meaning": join_text_lines(meaning_parts),
            "russian_example": join_text_lines(ru_lines),
            "english_example": join_text_lines(en_lines),
        })

    return entries


def audit_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify any suspicious entries or original source PDF typos for review."""
    suspicious = []
    for e in entries:
        issues = []
        # Check Latin characters in Russian word (PDF homoglyphs)
        lat_in_word = [c for c in e["russian_word"] if "a" <= c.lower() <= "z"]
        if lat_in_word:
            issues.append(f"Latin character(s) {lat_in_word} in Russian word '{e['russian_word']}' (Source PDF homoglyph)")

        # Check unbalanced parentheses / brackets in English meaning
        if e["english_meaning"].count("(") != e["english_meaning"].count(")"):
            issues.append(f"Unbalanced parentheses in English meaning: '{e['english_meaning']}'")
        if e["english_meaning"].count("[") != e["english_meaning"].count("]"):
            issues.append(f"Unbalanced square brackets in English meaning: '{e['english_meaning']}'")

        # Check Cyrillic characters in English example sentence
        cyr_in_en = [c for c in e["english_example"] if "\u0400" <= c <= "\u04ff"]
        if cyr_in_en:
            issues.append(f"Cyrillic character(s) {cyr_in_en} in English example: '{e['english_example']}'")

        # Check Latin characters in Russian example sentence (excluding Roman numerals)
        cleaned_ru = re.sub(r"\b[IVXLCDM]+\b", "", e["russian_example"])
        lat_in_ru = [c for c in cleaned_ru if "a" <= c.lower() <= "z"]
        if lat_in_ru:
            issues.append(f"Latin character(s) {lat_in_ru} in Russian example: '{e['russian_example']}'")

        if issues:
            suspicious.append({
                "number": e["number"],
                "russian_word": e["russian_word"],
                "issues": issues,
            })
    return suspicious


def find_default_pdf() -> str:
    """Find default PDF location."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "../2000_Most_Common_Russian_Words_in_Context_Get_Fluent_Increase_Your.pdf"),
        "/home/neo/Documents/2000_Most_Common_Russian_Words_in_Context_Get_Fluent_Increase_Your.pdf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return "/home/neo/Documents/2000_Most_Common_Russian_Words_in_Context_Get_Fluent_Increase_Your.pdf"


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_data_dir = os.path.join(base_dir, "data")
    
    parser = argparse.ArgumentParser(description="Extract Russian vocabulary from PDF into structured JSON.")
    parser.add_argument(
        "--pdf",
        default=find_default_pdf(),
        help="Path to input PDF file"
    )
    parser.add_argument(
        "--output",
        default=os.path.join(default_data_dir, "entries.json"),
        help="Path to output JSON file (default: data/entries.json)"
    )
    parser.add_argument(
        "--raw-output",
        default=os.path.join(default_data_dir, "raw.txt"),
        help="Path to output raw text file (default: data/raw.txt)"
    )
    parser.add_argument(
        "--report",
        default=os.path.join(default_data_dir, "review_report.json"),
        help="Path to output manual review report (default: data/review_report.json)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        raise FileNotFoundError(f"PDF file not found at: {args.pdf}")

    print(f"Opening PDF: {args.pdf}")
    doc = pymupdf.open(args.pdf)
    print(f"Total pages: {len(doc)}")

    print(f"Extracting raw text to '{args.raw_output}'...")
    extract_raw_text(doc, args.raw_output)
    print("Raw text saved successfully.")

    print("Extracting 2000 vocabulary entries...")
    entries = extract_entries(doc, start_page=12, end_page=404)
    print(f"Successfully extracted {len(entries)} entries.")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Clean dataset saved to '{args.output}'.")

    suspicious = audit_entries(entries)
    os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(suspicious, f, ensure_ascii=False, indent=2)
    print(f"Review report saved to '{args.report}'. Total suspicious items: {len(suspicious)}")


if __name__ == "__main__":
    main()
