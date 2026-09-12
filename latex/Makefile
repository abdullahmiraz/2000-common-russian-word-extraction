# Makefile for building 2000 Russian Words in Context Book

BUILD_DIR = build
OUTPUT_PDF = $(BUILD_DIR)/main.pdf
FINAL_PDF = $(BUILD_DIR)/2000_Most_Common_Russian_Words.pdf

.PHONY: all generate pdf clean

all: generate pdf

generate:
	python3 build_latex.py

pdf:
	mkdir -p $(BUILD_DIR)
	latexmk -xelatex -interaction=nonstopmode -output-directory=$(BUILD_DIR) main.tex
	cp $(OUTPUT_PDF) $(FINAL_PDF)
	@echo "=================================================="
	@echo "Build successful! PDF: $(FINAL_PDF)"
	@echo "=================================================="

clean:
	rm -rf $(BUILD_DIR)/*
	rm -f chapters/*.tex backmatter/*.tex
