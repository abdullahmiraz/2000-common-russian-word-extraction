#!/usr/bin/env python3
"""
Validator for Russian Vocabulary Dataset
Validates entries 1 to 2000 in entries.json for completeness, integrity, and consistency.
"""

import os
import sys
import re
import json
import argparse


def validate_dataset(json_path: str) -> bool:
    if not os.path.exists(json_path):
        print(f"[ERROR] Dataset file not found: {json_path}")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            entries = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON syntax in {json_path}: {e}")
            return False

    print("=" * 60)
    print(f"VALIDATING DATASET: {json_path}")
    print("=" * 60)

    total_count = len(entries)
    print(f"Total entries loaded: {total_count}")

    all_passed = True
    errors = []
    warnings = []

    # 1. Check total count
    if total_count != 2000:
        errors.append(f"Expected 2000 entries, but found {total_count}")
        all_passed = False

    # 2. Check number sequence and uniqueness
    numbers = [e.get("number") for e in entries if isinstance(e, dict) and "number" in e]
    num_set = set(numbers)
    expected_set = set(range(1, 2001))

    missing_nums = expected_set - num_set
    if missing_nums:
        errors.append(f"Missing numbers ({len(missing_nums)}): {sorted(list(missing_nums))[:20]}")
        all_passed = False

    duplicate_nums = [n for n in numbers if numbers.count(n) > 1]
    if duplicate_nums:
        unique_dups = sorted(list(set(duplicate_nums)))
        errors.append(f"Duplicate numbers ({len(unique_dups)}): {unique_dups[:20]}")
        all_passed = False

    # 3. Check field structure and non-empty content
    required_fields = [
        "number",
        "russian_word",
        "pronunciation",
        "english_meaning",
        "russian_example",
        "english_example",
    ]

    for idx, e in enumerate(entries):
        entry_num = e.get("number", f"index_{idx}")

        # Check missing fields
        for field in required_fields:
            if field not in e:
                errors.append(f"Entry {entry_num}: missing field '{field}'")
                all_passed = False
            elif e[field] is None or (isinstance(e[field], str) and not str(e[field]).strip()):
                errors.append(f"Entry {entry_num}: empty field '{field}'")
                all_passed = False

        # Type check
        if not isinstance(e.get("number"), int):
            errors.append(f"Entry {entry_num}: 'number' is not an integer ({type(e.get('number'))})")
            all_passed = False

        # Linguistic sanity checks
        ru_word = str(e.get("russian_word", ""))
        ru_ex = str(e.get("russian_example", ""))
        en_ex = str(e.get("english_example", ""))

        # Russian example should have Cyrillic letters
        has_cyr_ex = bool(re.search(r"[\u0400-\u04FF]", ru_ex))
        if not has_cyr_ex:
            errors.append(f"Entry {entry_num}: Russian example contains no Cyrillic characters")
            all_passed = False

        # English example should have Latin letters
        has_lat_ex = bool(re.search(r"[a-zA-Z]", en_ex))
        if not has_lat_ex:
            errors.append(f"Entry {entry_num}: English example contains no Latin characters")
            all_passed = False

        # Flag known source anomalies as warnings
        lat_in_word = [c for c in ru_word if "a" <= c.lower() <= "z"]
        if lat_in_word:
            warnings.append(f"Entry {entry_num}: Russian word '{ru_word}' has Latin char(s) {lat_in_word} (source PDF homoglyph)")

        cyr_in_en = [c for c in en_ex if "\u0400" <= c <= "\u04ff"]
        if cyr_in_en:
            warnings.append(f"Entry {entry_num}: English example has Cyrillic char(s) {cyr_in_en}")

    # Output results
    print("-" * 60)
    print("VALIDATION SUMMARY:")
    if errors:
        print(f"[FAIL] Found {len(errors)} error(s):")
        for err in errors[:30]:
            print(f"  - {err}")
        if len(errors) > 30:
            print(f"  ... and {len(errors) - 30} more errors.")
    else:
        print("[PASS] All 2000 entries (1 to 2000) are present, unique, and strictly structured.")
        print("[PASS] All required fields are present and non-empty.")
        print("[PASS] Zero missing entries, zero duplicate numbers.")

    print("-" * 60)
    print(f"SOURCE AUDIT FINDINGS: {len(warnings)} item(s) found in source PDF text:")
    for warn in warnings:
        print(f"  * {warn}")
    print("=" * 60)

    return all_passed


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_json = os.path.join(base_dir, "data", "entries.json")
    if not os.path.exists(default_json):
        default_json = os.path.join(base_dir, "entries.json")

    parser = argparse.ArgumentParser(description="Validate Russian vocabulary dataset.")
    parser.add_argument(
        "--file",
        default=default_json,
        help="Path to entries.json to validate (default: data/entries.json)"
    )
    args = parser.parse_args()

    passed = validate_dataset(args.file)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
