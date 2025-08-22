# Code Quality Analysis Tool Specification

## 1. Overview

This document outlines the plan for a lightweight, extensible, command-line tool to analyze various codebases and provide basic quality metrics. The tool is designed as a wrapper that can incorporate different language-specific static analysis tools.

## 2. Core Architecture

The tool uses a **pluggable analyzer pattern**. The core application is written in Python 3 and acts as an orchestrator. It is responsible for parsing command-line arguments, finding files, and invoking the appropriate language-specific analysis engine. This design allows for easy extension to new languages.

- **Orchestration Language:** Python 3
- **Analysis Engines:** Language-specific command-line tools.

## 3. Supported Languages & Engines

The tool's support for a language is dependent on having a suitable analysis engine.

### 3.1. Ruby
- **Engine:** `flog`
- **Prerequisites:** Ruby, `gem install flog`
- **File Discovery:** Finds `*.rb` files.

### 3.2. Golang
- **Engine:** `gocyclo`
- **Prerequisites:** Go, `go install github.com/fzipp/gocyclo/cmd/gocyclo@latest`, and the Go bin directory in the system PATH.
- **File Discovery:** Finds `*.go` files.

## 4. CLI Interface

The tool will be enhanced to accept a language specifier.

`python -m code_analyzer DIRECTORY --language [ruby|golang]`

- In the future, the `--language` flag may become optional as the tool could auto-detect the project type.

## 5. Unified Metrics

Regardless of the language, the tool will calculate and report on a unified set of metrics:

- **Lines of Code (LOC):** Total lines in all analyzed files.
- **Complexity Score:** A normalized score from the underlying engine (`flog`, `detekt`, etc.).
- **95th Percentile Complexity:** The average complexity of the most complex 5% of files.

## 6. Future Enhancements

- **Auto-detection** of project language based on file types (e.g., `Gemfile` vs. `build.gradle.kts`).
- **Code Duplication Analysis** by integrating tools like `flay` (for Ruby) or using `detekt`'s built-in capabilities.
- **Flexible Output Formats:** Add options to export results to JSON or HTML.
- **CI/CD Integration:** Provide examples and guidance for using the tool in a CI/CD pipeline.

## 7. Project Structure

The project structure remains the same, but the `analysis.py` file will be refactored to support multiple analyzers.

```
/
|-- code_analyzer/
|   |-- __init__.py
|   |-- __main__.py       # Main CLI entry point
|   |-- analysis.py     # Will contain language-specific modules
|-- requirements.txt
|-- README.md
|-- SPEC.md
```
