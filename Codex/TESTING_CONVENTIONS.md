# Testing Conventions
**Purpose:** Define the standard file pattern for every computational validation test in this repository.

## Per-Test Folder Pattern

Every test folder should follow this structure:

```text
tests/
  T##_test_name/
    README.md
    test.py
    test.md
    mistakes.log
    results/
      results.json
      results.md
```

## What Each File Is For

- `README.md`
  - Human overview
  - claim being tested
  - pass/fail criteria
  - kill condition
  - canonical inputs used
- `test.py`
  - executable Python source
  - honest implementation only
  - no hidden tuning to force a pass
- `test.md`
  - Markdown copy of the Python script or script logic
  - intended for readers who cannot run Python
  - should stay aligned with `test.py`
- `mistakes.log`
  - append-only log of coding errors, equation issues, fixes attempted, and unresolved problems
- `results/results.json`
  - machine-readable outputs
- `results/results.md`
  - plain-English summary of what ran, what happened, and whether the framework survived the test

## Allowed Changes During Testing

- Small non-structural fixes are allowed when the implementation is clearly wrong.
- Small non-structural equation cleanup is allowed when it preserves the canonical claim and improves correctness.
- Structural changes are **not** allowed silently.
- If a structural issue appears, stop, document it, and escalate it.

## Result Writing Rule

Each test must clearly separate:

1. What the code did
2. What the output was
3. What that output means
4. Whether the issue was coding error, parameter error, or framework-level failure

## Markdown Mirror Rule

The Markdown version is not optional. Every important test should be understandable even by a reader who never opens Python.

## Canonical Inputs

Current likely core inputs include:

- `canonical/CODEX_TEST_BRIEFING.md`
- `canonical/MASTER_TEST_STACK.md`
- `canonical/NO_DRIFT_CANONICAL_LAWS.md`
- `canonical/NODRIFT_LOSSLESS_v24.yaml`
- `canonical/THE_ONE_VARIABLE.md`
- `canonical/FORMAL_LAYER_PART1.md`
- `canonical/FORMAL_LAYER_PART2.md`
