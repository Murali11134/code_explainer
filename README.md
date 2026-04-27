# code_explainer

A project to analyze and explain code in a repository.

## Roadmap

- Stage 1 (current): Explain code flow **without AI**.
- Stage 2: Add AI-powered visual representation of code.
- Stage 3: Expand support to both Python and Java.
- Stage 4: Full-codebase explanation with security-aware handling for sensitive information.

## Stage 1 delivered

This stage now includes a CLI tool that performs static analysis for Python code and outputs:

- files scanned
- top-level classes and functions
- method/function arguments
- called functions/methods
- count of loops, conditionals, and return statements

## Usage

Run from the repository root:

```bash
python -m code_explainer.cli .
```

Or install as a local CLI:

```bash
pip install -e .
code-explainer .
```

Save output to a file:

```bash
python -m code_explainer.cli . --output flow_report.txt
```
