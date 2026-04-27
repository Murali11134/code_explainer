from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from code_explainer.analyzer import (
    analyze_python_file,
    collect_python_files,
    render_flow_report_json,
)


class AnalyzerTests(unittest.TestCase):
    def test_analyze_python_file_collects_imports_and_flow(self) -> None:
        source = """
import os
from pathlib import Path


def top(a):
    if a:
        return Path(str(a))
    return None


class Demo:
    def run(self, items):
        for item in items:
            print(item)
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "sample.py"
            file_path.write_text(source, encoding="utf-8")

            flow = analyze_python_file(file_path)

        self.assertEqual(flow.imports, ["from pathlib import Path", "os"])
        self.assertEqual(len(flow.functions), 1)
        self.assertEqual(flow.functions[0].name, "top")
        self.assertEqual(flow.functions[0].conditionals, 1)
        self.assertEqual(flow.functions[0].returns, 2)
        self.assertEqual(len(flow.classes), 1)
        self.assertEqual(flow.classes[0].methods[0].loops, 1)

    def test_collect_python_files_ignores_common_generated_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "keep.py").write_text("print('ok')\n", encoding="utf-8")
            (root / ".venv").mkdir()
            (root / ".venv" / "skip.py").write_text("print('skip')\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "skip.py").write_text("print('skip')\n", encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "skip.py").write_text("print('skip')\n", encoding="utf-8")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "skip.py").write_text("print('skip')\n", encoding="utf-8")

            files = list(collect_python_files(root))

        self.assertEqual(files, [root / "keep.py"])

    def test_render_flow_report_json_contains_serialized_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "sample.py"
            file_path.write_text("def run():\n    return 1\n", encoding="utf-8")
            flow = analyze_python_file(file_path)

        report = render_flow_report_json([flow])

        self.assertIn('"path"', report)
        self.assertIn(str(file_path), report)
        self.assertIn('"functions"', report)


if __name__ == "__main__":
    unittest.main()
