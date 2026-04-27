from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

IGNORED_DIRECTORIES = {".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist"}


@dataclass
class FunctionFlow:
    name: str
    lineno: int
    args: list[str]
    is_async: bool = False
    calls: list[str] = field(default_factory=list)
    loops: int = 0
    conditionals: int = 0
    returns: int = 0


@dataclass
class ClassFlow:
    name: str
    lineno: int
    methods: list[FunctionFlow] = field(default_factory=list)


@dataclass
class FileFlow:
    path: Path
    imports: list[str] = field(default_factory=list)
    classes: list[ClassFlow] = field(default_factory=list)
    functions: list[FunctionFlow] = field(default_factory=list)


class _FunctionVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.loops = 0
        self.conditionals = 0
        self.returns = 0

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.loops += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.loops += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.conditionals += 1
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self.returns += 1
        self.generic_visit(node)


def _collect_function_flow(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionFlow:
    visitor = _FunctionVisitor()
    visitor.visit(node)
    return FunctionFlow(
        name=node.name,
        lineno=node.lineno,
        args=_format_arguments(node.args),
        is_async=isinstance(node, ast.AsyncFunctionDef),
        calls=sorted(set(visitor.calls)),
        loops=visitor.loops,
        conditionals=visitor.conditionals,
        returns=visitor.returns,
    )


def _format_arguments(arguments: ast.arguments) -> list[str]:
    formatted: list[str] = []

    for arg in arguments.posonlyargs:
        formatted.append(arg.arg)
    if arguments.posonlyargs:
        formatted.append("/")

    for arg in arguments.args:
        formatted.append(arg.arg)

    if arguments.vararg:
        formatted.append(f"*{arguments.vararg.arg}")
    elif arguments.kwonlyargs:
        formatted.append("*")

    for arg in arguments.kwonlyargs:
        formatted.append(arg.arg)

    if arguments.kwarg:
        formatted.append(f"**{arguments.kwarg.arg}")

    return formatted


def _collect_imports(tree: ast.Module) -> list[str]:
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for imported in node.names:
                imports.append(imported.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(alias.name for alias in node.names)
            imports.append(f"from {module} import {names}" if module else f"from . import {names}")
    return sorted(set(imports))


def analyze_python_file(path: Path) -> FileFlow:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    flow = FileFlow(path=path, imports=_collect_imports(tree))

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_flow = ClassFlow(name=node.name, lineno=node.lineno)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    class_flow.methods.append(_collect_function_flow(child))
            flow.classes.append(class_flow)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            flow.functions.append(_collect_function_flow(node))

    return flow


def collect_python_files(root: Path) -> Iterable[Path]:
    for file in sorted(root.rglob("*.py")):
        if any(part in IGNORED_DIRECTORIES for part in file.parts):
            continue
        if file.name.startswith("."):
            continue
        yield file


def render_flow_report(file_flows: list[FileFlow]) -> str:
    lines: list[str] = []

    for file_flow in file_flows:
        lines.append(f"# {file_flow.path}")
        imports = ", ".join(file_flow.imports) if file_flow.imports else "none"
        lines.append(f"  - imports: {imports}")

        if not file_flow.classes and not file_flow.functions:
            lines.append("  - No top-level classes or functions found")
            lines.append("")
            continue

        for class_flow in file_flow.classes:
            lines.append(f"  - class {class_flow.name} (line {class_flow.lineno})")
            if not class_flow.methods:
                lines.append("    - no methods")
            for method in class_flow.methods:
                lines.extend(_render_function(method, prefix="    "))

        for function in file_flow.functions:
            lines.extend(_render_function(function, prefix="  "))

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_flow_report_json(file_flows: list[FileFlow]) -> str:
    payload = []
    for file_flow in file_flows:
        entry = asdict(file_flow)
        entry["path"] = str(file_flow.path)
        payload.append(entry)
    return json.dumps(payload, indent=2) + "\n"


def _render_function(function: FunctionFlow, prefix: str) -> list[str]:
    args = ", ".join(function.args) if function.args else "(no args)"
    calls = ", ".join(function.calls) if function.calls else "none"
    signature = "async def" if function.is_async else "def"
    return [
        f"{prefix}- {signature} {function.name}({args}) [line {function.lineno}]",
        f"{prefix}  - calls: {calls}",
        f"{prefix}  - loops: {function.loops}, conditionals: {function.conditionals}, returns: {function.returns}",
    ]
