# Empirical Data

This directory contains the issue dataset and the main results of our study.

## Issue Dataset

File `all_issues.json`: 33,650 potential bug reports in JSON format.

## Analysis Results

File `analyzed_issues.csv` contains all bug reports we have analyzed. The field "label" could be "Invalid" (excluded issues), "Negative" (issues report bugs that do not violate commonsense), "Positive" (issues report commonsense-violating bugs).

File `principles.html` is a self-contained webpage that presents all commonsense principles we have identified from the commonsense-violating bugs.
