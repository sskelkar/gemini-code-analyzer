import argparse
import sys
from . import analysis

def print_report(report):
    """Prints the final analysis report to the console."""
    print("\n\n--- Code Quality Report ---")

    if not report or not report.get("summary"):
        print("Could not analyze any files.")
        return

    summary = report["summary"]
    file_scores = report["file_scores"]

    print(f"\nOverall Metrics for {report.get('language').capitalize()}:")
    print(f"  - Total Files Analyzed: {summary.get('total_files', 0)}")
    print(f"  - Total Lines of Code:  {summary.get('total_loc', 0)}")
    print(f"  - Average Complexity:   {summary.get('average_complexity', 0):.2f}")
    print(f"  - 95th Percentile Avg:  {summary.get('percentile_95_complexity', 0):.2f} (Avg. of worst 5%)")

    print("\nTop 5 Most Complex Files:")
    for path, score in file_scores[:5]:
        print(f"{score:>8.1f}: {path}")
    print("\n")

def main():
    """
    The main entry point for the command-line tool.
    """
    parser = argparse.ArgumentParser(
        description="An extensible code quality analysis tool."
    )
    parser.add_argument(
        "directory",
        metavar="DIRECTORY",
        type=str,
        help="The path to the project directory to analyze.",
    )
    parser.add_argument(
        "--language",
        type=str,
        required=True,
        choices=["ruby"], # Add 'kotlin' here when implemented
        help="The programming language of the project."
    )
    args = parser.parse_args()

    print(f"Analyzing {args.language.capitalize()} project in: {args.directory}")
    
    report = analysis.run_analysis(args.language, args.directory)

    if report.get("error"):
        print(f"\nError: {report['error']}", file=sys.stderr)
        return 1

    print_report(report)

if __name__ == "__main__":
    sys.exit(main())
