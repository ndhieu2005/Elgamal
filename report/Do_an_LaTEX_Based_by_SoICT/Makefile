# Makefile for DoAn.tex
# Run from this directory: report/Do_an_LaTEX_Based_by_SoICT/
#
# Targets:
#   make          — compile DoAn.pdf (default)
#   make pdf      — same as above
#   make clean    — remove aux files, keep DoAn.pdf
#   make cleanall — remove aux files AND DoAn.pdf
#   make watch    — continuous preview mode
#
# Requirements: latexmk, pdflatex, biber (TeX Live full or MiKTeX full)
# Windows: install GNU Make via Chocolatey: choco install make

MAIN      := DoAn
LATEXMK   := latexmk
LMKFLAGS  := -pdf -pdflatex="pdflatex -synctex=1 -interaction=nonstopmode" -bibtex -use-make

.PHONY: all pdf clean cleanall watch

all: pdf

pdf: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex
	$(LATEXMK) $(LMKFLAGS) $(MAIN).tex

clean:
	$(LATEXMK) -c $(MAIN).tex

cleanall:
	$(LATEXMK) -C $(MAIN).tex

watch:
	$(LATEXMK) $(LMKFLAGS) -pvc $(MAIN).tex
