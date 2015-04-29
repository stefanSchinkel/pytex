README
======

###Name

pytex

###SYNOPSIS

   `pytex texFile [options]`

###DESCRIPTION


A thin wrapper for pdflatex and bibtex. It will
run pdflatex on the input file and re-compile it
if needed (eg to fix cross references). If necessary
it will call bibtex to compile the bibliography from
the correponding auxiliary file.

The following option are available

  * `-h` `--help` print  help
  * `-o` string passed to the pdflatex binary (-o)
  * `--options` string passed to the pdflatex binary (long option)
  * `-b --bibtex` force bibtex runrunning pdflatex
  * `-r` remove auxiliary files, removes all auxiliary files *BEFORE* compiling the input file except for file.bib
