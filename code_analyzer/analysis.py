import glob
import os
import subprocess
import math

# --- Language-Specific Implementations --- #

def _find_ruby_files(directory):
    """Find all Ruby (.rb) files in a given directory."""
    search_path = os.path.join(directory, "**", "*.rb")
    return glob.glob(search_path, recursive=True)

def _run_flog_on_file(file_path):
    """Run the flog tool on a single file and return the raw output."""
    try:
        result = subprocess.run(
            ["flog", "-c", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout, None
    except FileNotFoundError:
        return None, "'flog' command not found. Please ensure Ruby and the flog gem are installed."
    except subprocess.CalledProcessError as e:
        return None, f"Error running flog on {file_path}: {e.stderr}"

def _parse_flog_total(flog_text):
    """Parse the raw text output from flog to get the total score."""
    try:
        first_line = flog_text.strip().split('\n')[0]
        return float(first_line.strip().split(':')[0])
    except (ValueError, IndexError):
        return None

# --- Analyzer Configuration (Strategy Pattern) --- #

ANALYZER_CONFIG = {
    "ruby": {
        "file_finder": _find_ruby_files,
        "analyzer_func": _run_flog_on_file,
        "parser_func": _parse_flog_total,
    },
    # "kotlin": {
    #     "file_finder": _find_kotlin_files,
    #     "analyzer_func": _run_detekt_on_file,
    #     "parser_func": _parse_detekt_output,
    # },
}

# --- Generic Analysis Orchestrator --- #

def _get_loc(file_path):
    """Calculate the lines of code (LOC) for a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except IOError:
        return 0

def _calculate_summary(file_scores, total_loc):
    """Calculate summary metrics from a list of (file, score) tuples."""
    if not file_scores:
        return {}

    scores = [score for _, score in file_scores]
    total_files = len(scores)
    percentile_index = math.ceil(total_files * 0.05)
    
    # Sort by score to find top 5%
    file_scores.sort(key=lambda item: item[1], reverse=True)
    top_5_percent_scores = [score for _, score in file_scores[:percentile_index]]
    percentile_avg = sum(top_5_percent_scores) / len(top_5_percent_scores) if top_5_percent_scores else 0

    return {
        "total_files": total_files,
        "total_loc": total_loc,
        "average_complexity": sum(scores) / total_files,
        "percentile_95_complexity": percentile_avg,
    }

def run_analysis(language, directory):
    """Main entry point for analysis. Dispatches to the correct language analyzer."""
    if language not in ANALYZER_CONFIG:
        return {"error": f"Language '{language}' is not supported."}

    config = ANALYZER_CONFIG[language]
    files = config["file_finder"](directory)
    if not files:
        return {"error": "No source files found in the specified directory."}

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

    summary = _calculate_summary(file_scores, total_loc)
    # Sort for final report display
    file_scores.sort(key=lambda item: item[1], reverse=True)

    return {
        "language": language,
        "summary": summary,
        "file_scores": file_scores,
    }
