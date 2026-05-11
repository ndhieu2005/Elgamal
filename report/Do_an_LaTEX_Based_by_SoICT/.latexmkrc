# .latexmkrc — latexmk configuration for DoAn.tex
# Place this file in report/Do_an_LaTEX_Based_by_SoICT/

# -------------------------------------------------------
# Compiler settings
# -------------------------------------------------------

# Use pdflatex (mode 1). Do NOT change to 4 (lualatex) or 5 (xelatex).
$pdf_mode = 1;

$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode %O %S';

# Use biber as bibliography backend (matches \usepackage[backend=biber]{biblatex})
$bibtex_use = 2;

# -------------------------------------------------------
# Glossaries support
# -------------------------------------------------------
# When \printnoidxglossaries is re-enabled, pdflatex writes .glo files.
# These rules tell latexmk to run makeglossaries automatically.

add_cus_dep('glo', 'gls', 0, 'run_makeglossaries');
add_cus_dep('acn', 'acr', 0, 'run_makeglossaries');

sub run_makeglossaries {
    my ($base_name, $path) = fileparse( $_[0] );
    pushd $path;
    my $return = system "makeglossaries '$base_name'";
    popd;
    return $return;
}

# -------------------------------------------------------
# Clean rules
# -------------------------------------------------------
push @generated_exts, 'glo', 'gls', 'glg', 'acn', 'acr', 'alg', 'ist';
push @generated_exts, 'run.xml', 'bcf', 'bbl';

# -------------------------------------------------------
# Do NOT set $out_dir.
# \subfile with relative \graphicspath{Hinhve/} breaks when
# PDF output is written to a separate directory.
# -------------------------------------------------------
