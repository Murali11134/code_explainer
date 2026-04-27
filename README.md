# code_explainer

A project to analyze and explain code in a repository.

## Roadmap

- Stage 1 (current): Explain code flow **without AI**.
- Stage 2: Add AI-powered visual representation of code.
- Stage 3: Expand support to both Python and Java.
- Stage 4: Full-codebase explanation with security-aware handling for sensitive information.

## Stage 1 delivered

This stage includes a small CLI tool that performs static analysis for Python code and outputs:

- files scanned
- imports per file
- top-level classes and functions
- method/function arguments
- called functions/methods
- count of loops, conditionals, and return statements

Ignored folders during scan:

- `.venv`
- `__pycache__`
- `.git`
- `node_modules`

## Usage

Run from the repository root:

```bash
python -m code_explainer.cli .
```

Select output format:

```bash
python -m code_explainer.cli . --format text
python -m code_explainer.cli . --format json
```

Or install as a local CLI:

```bash
pip install -e .
code-explainer . --format json
```

Save output to a file:

```bash
python -m code_explainer.cli . --format json --output flow_report.json
```

## Sample output (text)

```text
# /repo/example.py
  - imports: from pathlib import Path, os
  - class Demo (line 8)
    - def run(self, items) [line 9]
      - calls: print
      - loops: 1, conditionals: 0, returns: 0
  - def top(a) [line 3]
    - calls: Path, str
    - loops: 0, conditionals: 1, returns: 2
```

## Sample output (json)

```json
[
  {
    "path": "/repo/example.py",
    "imports": ["from pathlib import Path", "os"],
    "classes": [],
    "functions": [
      {
        "name": "top",
        "lineno": 3,
        "args": ["a"],
        "calls": ["Path", "str"],
        "loops": 0,
        "conditionals": 1,
        "returns": 2
      }
    ]
  }
]
```
