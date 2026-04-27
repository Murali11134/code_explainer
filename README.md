# code_explainer

A beginner-friendly project to analyze and explain Python code flow in a repository.

## Roadmap

- Stage 1 (current): Explain code flow **without AI**.
- Stage 2: Add AI-powered visual representation of code.
- Stage 3: Expand support to both Python and Java.
- Stage 4: Full-codebase explanation with security-aware handling for sensitive information.

## Stage 1 features (non-AI)

The CLI performs static analysis for Python files and reports:

- imports per file
- top-level classes and functions
- function/method signatures (including `*args`, `**kwargs`, keyword-only args, and async functions)
- called functions/methods
- count of loops, conditionals, and return statements

Ignored folders during scan:

- `.git`
- `.venv`
- `venv`
- `__pycache__`
- `node_modules`
- `build`
- `dist`

## Usage

Run from repository root:

```bash
python -m code_explainer.cli .
```

Choose output format:

```bash
python -m code_explainer.cli . --format text
python -m code_explainer.cli . --format json
```

Save output to file:

```bash
python -m code_explainer.cli . --format json --output flow_report.json
```

## Sample input

`example.py`

```python
import os
from pathlib import Path


def transform(value, *args, mode="safe", **kwargs):
    if value:
        return Path(str(value))
    return None


async def fetch_data(client, *, retries=2):
    return await client.get("/items")
```

## Sample output (text)

```text
# /repo/example.py
  - imports: from pathlib import Path, os
  - def transform(value, *args, mode, **kwargs) [line 5]
    - calls: Path, str
    - loops: 0, conditionals: 1, returns: 2
  - async def fetch_data(client, *, retries) [line 11]
    - calls: get
    - loops: 0, conditionals: 0, returns: 1
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
        "name": "transform",
        "lineno": 5,
        "args": ["value", "*args", "mode", "**kwargs"],
        "is_async": false,
        "calls": ["Path", "str"],
        "loops": 0,
        "conditionals": 1,
        "returns": 2
      },
      {
        "name": "fetch_data",
        "lineno": 11,
        "args": ["client", "*", "retries"],
        "is_async": true,
        "calls": ["get"],
        "loops": 0,
        "conditionals": 0,
        "returns": 1
      }
    ]
  }
]
```
