#!/usr/bin/env python3
"""Run every executable test script under Codex/tests and compile a run report.

This runner is intentionally conservative: it reports whether scripts execute,
and separately reports whether each test appears to be implemented or still a
scaffold placeholder.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
COMPILED_DIR = ROOT / "compiled_results"


@dataclass
class TestRun:
    test_id: str
    script: str
    returncode: int
    implemented: bool
    status: str
    duration_s: float
    stdout: str
    stderr: str


def is_scaffold(script_text: str) -> bool:
    lowered = script_text.lower()
    return "scaffold" in lowered or "populate this file" in lowered


def run_one(script_path: Path) -> TestRun:
    script_text = script_path.read_text(encoding="utf-8")
    implemented = not is_scaffold(script_text)

    started = datetime.now(timezone.utc)
    proc = subprocess.run(
        ["python3", str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT.parent),
        check=False,
    )
    ended = datetime.now(timezone.utc)

    if proc.returncode == 0 and implemented:
        status = "PASS"
    elif proc.returncode == 0 and not implemented:
        status = "SCAFFOLD_ONLY"
    else:
        status = "FAIL"

    return TestRun(
        test_id=script_path.parent.name,
        script=str(script_path.relative_to(ROOT.parent)),
        returncode=proc.returncode,
        implemented=implemented,
        status=status,
        duration_s=(ended - started).total_seconds(),
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
    )


def write_per_test_results(result: TestRun) -> None:
    test_dir = TESTS_DIR / result.test_id / "results"
    test_dir.mkdir(parents=True, exist_ok=True)

    payload = asdict(result)
    (test_dir / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        f"# {result.test_id} Results",
        "",
        f"- Status: **{result.status}**",
        f"- Return code: `{result.returncode}`",
        f"- Implemented logic present: `{result.implemented}`",
        f"- Runtime: `{result.duration_s:.3f}s`",
    ]
    if result.stderr:
        md.extend(["", "## stderr", "", "```", result.stderr, "```"])
    if result.stdout:
        md.extend(["", "## stdout", "", "```", result.stdout, "```"])

    (test_dir / "results.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def parse_master_test_count() -> int:
    master = (ROOT / "canonical" / "MASTER_TEST_STACK.md").read_text(encoding="utf-8")
    marker = "MASTER EQUATION TESTS ("
    idx = master.find(marker)
    if idx == -1:
        return -1
    tail = master[idx + len(marker): idx + len(marker) + 32]
    digits = "".join(ch for ch in tail if ch.isdigit())
    return int(digits) if digits else -1


def write_compiled_report(results: List[TestRun]) -> None:
    COMPILED_DIR.mkdir(parents=True, exist_ok=True)

    total_master_tests = parse_master_test_count()
    executed = len(results)
    failed = sum(1 for r in results if r.status == "FAIL")
    scaffold_only = sum(1 for r in results if r.status == "SCAFFOLD_ONLY")
    passed_implemented = sum(1 for r in results if r.status == "PASS")

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "master_stack_total_tests": total_master_tests,
        "executed_test_scripts": executed,
        "passed_implemented": passed_implemented,
        "scaffold_only": scaffold_only,
        "failed": failed,
        "results": [asdict(r) for r in results],
    }
    (COMPILED_DIR / "gauntlet_results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    lines = [
        "# Gauntlet Run Results",
        "",
        f"Generated (UTC): {payload['generated_at_utc']}",
        "",
        f"Master stack tests listed: **{total_master_tests}**",
        f"Executable test scripts found in repo: **{executed}**",
        f"Implemented tests passed: **{passed_implemented}**",
        f"Scaffold-only scripts executed: **{scaffold_only}**",
        f"Failed scripts: **{failed}**",
        "",
        "| Test | Status | Implemented | Return code | Runtime (s) |",
        "|---|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r.test_id} | {r.status} | {str(r.implemented)} | {r.returncode} | {r.duration_s:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Note",
            "",
            "`SCAFFOLD_ONLY` means the script runs but still contains placeholder scaffold text",
            "instead of the full computational test implementation.",
        ]
    )
    (COMPILED_DIR / "master_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scripts = sorted(TESTS_DIR.glob("T*/test.py"))
    results = [run_one(path) for path in scripts]

    for result in results:
        write_per_test_results(result)
    write_compiled_report(results)


if __name__ == "__main__":
    main()
