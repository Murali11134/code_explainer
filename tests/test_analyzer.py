from __future__ import annotations

import json
from pathlib import Path

from code_explainer.analyzer import analyze_python_file, collect_python_files, render_flow_report_json


def test_analyze_python_file_collects_imports_and_extended_args(tmp_path: Path) -> None:
    source = """
import os
from pathlib import Path


def top(a, *args, flag=False, **kwargs):
    if a:
        return Path(str(a))
    return None


async def worker(data, *, retries=1):
    return data


class Demo:
    async def run(self, items, /, *args, limit=1, **kwargs):
        for item in items:
            print(item)
"""
    file_path = tmp_path / "sample.py"
    file_path.write_text(source, encoding="utf-8")

    flow = analyze_python_file(file_path)

    assert flow.imports == ["from pathlib import Path", "os"]

    top = flow.functions[0]
    assert top.name == "top"
    assert top.args == ["a", "*args", "flag", "**kwargs"]
    assert top.conditionals == 1
    assert top.returns == 2

    worker = flow.functions[1]
    assert worker.name == "worker"
    assert worker.is_async is True
    assert worker.args == ["data", "*", "retries"]

    method = flow.classes[0].methods[0]
    assert method.is_async is True
    assert method.args == ["self", "items", "/", "*args", "limit", "**kwargs"]
    assert method.loops == 1


def test_collect_python_files_ignores_common_generated_folders(tmp_path: Path) -> None:
    (tmp_path / "keep.py").write_text("print('ok')\n", encoding="utf-8")

    for folder in [".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist"]:
        folder_path = tmp_path / folder
        folder_path.mkdir(parents=True)
        (folder_path / "skip.py").write_text("print('skip')\n", encoding="utf-8")

    files = list(collect_python_files(tmp_path))

    assert files == [tmp_path / "keep.py"]


def test_render_flow_report_json_contains_serialized_path(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.py"
    file_path.write_text("def run():\n    return 1\n", encoding="utf-8")
    flow = analyze_python_file(file_path)

    report = render_flow_report_json([flow])
    payload = json.loads(report)

    assert payload[0]["path"] == str(file_path)
    assert payload[0]["functions"][0]["name"] == "run"
