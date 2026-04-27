from __future__ import annotations

import json
from pathlib import Path

from code_explainer import cli


def test_cli_outputs_text_by_default(tmp_path: Path, capsys) -> None:
    (tmp_path / "app.py").write_text("def run(name):\n    return name\n", encoding="utf-8")

    cli.main([str(tmp_path)])
    output = capsys.readouterr().out

    assert "# " in output
    assert "- def run(name)" in output


def test_cli_outputs_json_when_requested(tmp_path: Path, capsys) -> None:
    (tmp_path / "app.py").write_text("import os\n\ndef run():\n    return os.getcwd()\n", encoding="utf-8")

    cli.main([str(tmp_path), "--format", "json"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload[0]["imports"] == ["os"]
    assert payload[0]["functions"][0]["name"] == "run"


def test_cli_writes_output_file(tmp_path: Path, capsys) -> None:
    (tmp_path / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
    output_path = tmp_path / "report.json"

    cli.main([str(tmp_path), "--format", "json", "--output", str(output_path)])
    stdout = capsys.readouterr().out

    assert output_path.exists()
    assert "Report written to" in stdout
