#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import getopt

__version__ = "0.2"


def printHelp():
    """
    Prints the help message.
    """
    help_str = """
NAME
   pytex
SYNOPSIS
   pytex file [options]
DESCRIPTION
   A thin wrapper for pdflatex and bibtex. It will
   run pdflatex on the input file and re-compile it
   if needed (eg to fix cross references). If necessary
   it will call bibtex to compile the bibliography from
   the correponding auxiliary file.

   The following option are available

   -h --help    print this help

   -o --options opt
    string with an option passed to the pdflatex binary
    Use -o of short and --option for long options

   -b --bibtex
    force bibtex to be run even if no bibtex
    warning is issued when running pdflatex

   -r   remove auxiliary files, will remove all
    auxiliary files BEFORE compiling the input file
    except for file.bib

"""
    print(help_str)


def runLatex(file, opt=''):
    """
    This function opens a pipe to the pdflatex binary,
    compiles the file & parses the log.
    """

    # assemble command and force latex to run non-stop
    if len(opt) > 0:
        cmd = "pdflatex " + opt + " -interaction=nonstopmode " + texFile
    else:
        cmd = "pdflatex -interaction=nonstopmode " + texFile
    # empty logMessage, errorMessage & default errorCode
    logMessage = []
    errorMessage = []
    errorCode = 0

    # store log in list
    runLog = os.popen(cmd).readlines()

    # loop over list
    for i in range(len(runLog)):

        # get current line
        line = runLog[i]

        # this happens w/ the bloody APAcite
        if "NOT AUSTRALIAN!!!" in line:
            print("Apacite package used")
            errorCode = 0
            continue
        elif "Citation" in line:
            logMessage.append(line)
            errorCode = 2
            break  # also break if bibtex needs to be run
        elif "Warning" in line:
            # warnings have to be caught first
            # as changing of float specifiers is common
            # and those often contain a "!"
            logMessage.append(line)
            logMessage.append(runLog[i + 1])
            errorCode = 3
            continue
        elif "!" in line:
            errorMessage.append(line)
            errorMessage.append(runLog[i + 1])
            errorCode = 1
            break   # on a real error, break

    return (errorCode, errorMessage, logMessage)


def runBibtex(file):
    """
    Call bibtex on auxiliary file
    """

    print("Running bibTeX")
    cmd = "bibtex " + texFile[:-4] + ".aux"
    os.popen(cmd)


def printLog(logMessage):
    """
        shorthand for printing logs
    """
    for line in logMessage:
        print(line[:-2])


def parseArgs(args):
    """
    Check argv for input file, check
    file extension and return to caller
    """
    try:
        texFile = args[1]
    except IndexError:
        printHelp()
        exit(-1)

    # MY pdflatex is smart enough to deal with
    # extensionless TeX files others may not.
    if texFile.endswith(".tex"):
        pass
    # due to tabcompletion
    elif texFile.endswith("."):
        texFile = texFile + "tex"
    else:
        texFile = texFile + ".tex"

    if os.path.isfile(texFile):
        return texFile
    else:
        print("Error: Input file not found")
        sys.exit(-1)


def parseOpts(args):
    """
    Parse the input for options passed.
    Should be called on sys.argv[2:] only
    as sys.argv[1] is the tex file
    Supported options
    -h --help       : print help
    -o --options    : option for pdflatex binary
    -b --bibtex     : force bibTex
    -r              : remove auxiliary files
    """

    # set the defaults
    texOptions = ''
    flagForceBibtex = False
    flagRemoveAux = False

    opts, args = getopt.getopt(args, "hro:b", ["help", "options=", "bibtex"])

    for opt, arg in opts:

        if opt == "-h" or opt == "--help":
            printHelp()
            sys.exit(0)
        elif opt in ("-o"):
            texOptions = "-" + arg
        elif opt in ("--options"):
            texOptions = "--" + arg
        elif opt in ("-b", "--bibtex"):
            flagForceBibtex = True
        elif opt in ("-r"):
            flagRemoveAux = True

    # return in tuple
    return(texOptions, flagForceBibtex, flagRemoveAux)


if __name__ == '__main__':
    # runCounters
    latexRuns = 0
    bibtexRuns = 0

    # parse argv for filename
    texFile = parseArgs(sys.argv)

    # get options if given
    (texOptions, flagForceBibtex, flagRemoveAux) = parseOpts(sys.argv[2:])

    print("This is PyTeX Version: %s" % __version__)
    print("Running pdflatex " + texOptions + " on file:  " + texFile)

    # remove auxiliary files, if requested
    if flagRemoveAux is True:
        print("Removing auxiliary files")
        for file in os.listdir('.'):
            if file.startswith(texFile[:-4]) and file[-3:] not in ["bib", "tex"]:
                os.remove(file)

    # call function
    while (bibtexRuns < 3) and (latexRuns < 3):

        # compile tex
        (errorCode, errorMessage, logMessage) = runLatex(texFile, texOptions)

        # if requested, ensure that bibtex is run
        if flagForceBibtex is True:
            runBibtex(file)

        # increment latexCounter
        latexRuns += 1

        if errorCode == 0:
            # ignoreable warning such as apacite
            # package being used
            print("Successfully compiled " + texFile)
            break

        elif errorCode == 1:
            # critical error, has to be fixed in .tex file
            print("The following error(s) occured:")
            printLog(errorMessage)
            sys.exit(0)

        elif errorCode == 2:
            # some reference is not found, running bibtex is required
            runBibtex(file)
            bibtexRuns += 1

        elif errorCode == 3:
            # some warning that should be fixed on re-compile
            print("Latex warning. Recompiling.")
            pass

    # if we are here and the logMessage is not empty sth is messed up
    if len(logMessage):
        print("The following warning occurred.")
        printLog(logMessage)
