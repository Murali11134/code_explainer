from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_python_file, collect_python_files, render_flow_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-explainer",
        description="Stage 1 code explainer: static flow summary without AI.",
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("."),
        help="Repository or folder to analyze (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional file path to save the generated report.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    root = args.path.resolve()
    files = [f for f in collect_python_files(root) if f.is_file()]

    if not files:
        report = f"No Python files found in {root}\n"
    else:
        file_flows = [analyze_python_file(file) for file in files]
        report = render_flow_report(file_flows)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
