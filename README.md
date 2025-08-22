# Extensible Code Quality Analyzer

This tool analyzes codebases of various languages to provide code quality metrics. It is designed as a wrapper around popular, language-specific analysis tools.

## Prerequisites

This tool requires language-specific analyzers to be installed.

- **For Ruby analysis:**
    - Ruby
    - `flog` gem (`gem install flog`)

## Usage

The tool requires you to specify the language of the project you want to analyze.

```bash
# For a Ruby project
python -m code_analyzer /path/to/your/project --language ruby
```

## Metrics Reported

The tool provides the following metrics in its report:

### Overall Metrics

- **Total Files Analyzed:** The total number of source files found and analyzed in the target directory.
- **Total Lines of Code:** A sum of all lines from all analyzed files.
- **Average Complexity:** The average complexity score across all files. This gives a general sense of the project's complexity.
- **95th Percentile Avg:** The average complexity score of the most complex 5% of files. This metric is particularly useful for identifying systemic complexity and potential maintenance hotspots.

### Top 5 Most Complex Files

This is a list of the five files with the highest individual complexity scores. These files are often the best candidates for immediate refactoring.
