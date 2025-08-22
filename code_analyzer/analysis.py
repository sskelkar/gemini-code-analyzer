import glob
import os
import subprocess
import math
from collections import defaultdict

# --- Language-Specific Implementations --- #

# --- Ruby / Flog --- #
def _find_ruby_files(directory):
    search_path = os.path.join(directory, "**", "*.rb")
    return glob.glob(search_path, recursive=True)

def _run_flog_on_file(file_path):
    try:
        result = subprocess.run(["flog", "-c", file_path], capture_output=True, text=True, check=True)
        return result.stdout, None
    except FileNotFoundError:
        return None, "'flog' command not found. Please ensure Ruby and the flog gem are installed."
    except subprocess.CalledProcessError as e:
        return None, f"Error running flog on {file_path}: {e.stderr}"

def _parse_flog_total(flog_text):
    try:
        return float(flog_text.strip().split('\n')[0].strip().split(':')[0])
    except (ValueError, IndexError):
        return None

# --- Golang / Gocyclo --- #
def _find_go_files(directory):
    search_path = os.path.join(directory, "**", "*.go")
    return glob.glob(search_path, recursive=True)

def _run_gocyclo(directory):
    try:
        # Exclude vendor directories and test files which is a common practice
        result = subprocess.run(["gocyclo", "-avg", "-over", "0", "."], cwd=directory, capture_output=True, text=True, check=True)
        return result.stdout, None
    except FileNotFoundError:
        return None, "'gocyclo' command not found. Please ensure Go is installed and `gocyclo` is in your PATH."
    except subprocess.CalledProcessError as e:
        return None, f"Error running gocyclo: {e.stderr}"

def _parse_gocyclo_output(gocyclo_text):
    file_scores = defaultdict(int)
    for line in gocyclo_text.strip().split('\n'):
        try:
            parts = line.split()
            score = int(parts[0])
            file_path = parts[3].split(':')[0]
            # gocyclo runs from within the directory, so path is relative
            # We don't have the full path here, but it's sufficient for reporting
            file_scores[file_path] += score
        except (ValueError, IndexError):
            continue
    return list(file_scores.items())

# --- Analyzer Configuration (Strategy Pattern) --- #

ANALYZER_CONFIG = {
    "ruby": {
        "analysis_mode": "file-by-file",
        "file_finder": _find_ruby_files,
        "analyzer_func": _run_flog_on_file,
        "parser_func": _parse_flog_total,
    },
    "golang": {
        "analysis_mode": "project",
        "file_finder": _find_go_files,
        "analyzer_func": _run_gocyclo,
        "parser_func": _parse_gocyclo_output,
    },
}

# --- Generic Analysis Orchestrator --- #

def _get_loc(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except IOError:
        return 0

def _calculate_summary(file_scores, total_loc):
    if not file_scores:
        return {}
    scores = [score for _, score in file_scores]
    total_files = len(scores)
    percentile_index = math.ceil(total_files * 0.05)
    file_scores.sort(key=lambda item: item[1], reverse=True)
    top_5_percent_scores = [score for _, score in file_scores[:percentile_index]]
    percentile_avg = sum(top_5_percent_scores) / len(top_5_percent_scores) if top_5_percent_scores else 0
    return {
        "total_files": total_files,
        "total_loc": total_loc,
        "average_complexity": sum(scores) / total_files if scores else 0,
        "percentile_95_complexity": percentile_avg,
    }

def run_analysis(language, directory):
    if language not in ANALYZER_CONFIG:
        return {"error": f"Language '{language}' is not supported."}

    config = ANALYZER_CONFIG[language]
    analysis_mode = config["analysis_mode"]
    
    print(f"Running {language.capitalize()} analyzer ({analysis_mode} mode)...")

    if analysis_mode == "file-by-file":
        files = config["file_finder"](directory)
        if not files:
            return {"error": "No source files found."}
        file_scores = []
        total_loc = 0
        for file_path in files:
            output, err = config["analyzer_func"](file_path)
            if err:
                return {"error": err}
            score = config["parser_func"](output)
            if score is not None:
                file_scores.append((file_path, score))
                total_loc += _get_loc(file_path)
                print(f".", end="", flush=True)
    
    elif analysis_mode == "project":
        output, err = config["analyzer_func"](directory)
        if err:
            return {"error": err}
        file_scores = config["parser_func"](output)
        # Get total LOC for all found files
        files = config["file_finder"](directory)
        total_loc = sum(_get_loc(f) for f in files)

    else:
        return {"error": f"Unknown analysis mode: {analysis_mode}"}

    summary = _calculate_summary(file_scores, total_loc)
    file_scores.sort(key=lambda item: item[1], reverse=True)

    return {
        "language": language,
        "summary": summary,
        "file_scores": file_scores,
    }
