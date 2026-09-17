# [H] PraisonAI Code agent tools fail open without a workspace boundary

## Summary
Severity: High
Advisory: GHSA-gcq3-mfvh-3x25
CVE: CVE-2026-56839
CWE: CWE-200, CWE-22, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-gcq3-mfvh-3x25
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.6.59

## Details
# PraisonAI Code agent tools fail open without a workspace boundary

## Summary

PraisonAI Code's agent-compatible `CODE_TOOLS` wrappers keep a global workspace root initialized to `None`. If an application uses `CODE_TOOLS`, `code_read_file`, `code_search_replace`, or `code_apply_diff` before calling `set_workspace()`, the wrappers pass `workspace=None` into lower-level helpers that only enforce path containment when a workspace is truthy. Absolute paths outside the intended project workspace are then read and modified.

The official examples correctly call `set_workspace()` before `CODE_TOOLS`, and this report does not claim configured workspaces are ineffective. The issue is the fail-open default. PraisonAI's security documentation describes workspace boundaries as the path-traversal protection mechanism, and the already-published Python API arbitrary file write advisory (`GHSA-hvhp-v2gc-268q`) was fixed by defaulting an unset workspace to `os.getcwd()`. The adjacent read and edit paths reached through `CODE_TOOLS` still fail open.

## Affected Components

- Package: `praisonai`
- Current upstream main tested: `2f9677abb2ea68eab864ee8b6a828fd0141612e1`
- Latest tested release: `v4.6.57`
- Primary files:
  - `src/praisonai/praisonai/code/agent_tools.py`
  - `src/praisonai/praisonai/code/tools/read_file.py`
  - `src/praisonai/praisonai/code/tools/search_replace.py`
  - `src/praisonai/praisonai/code/tools/apply_diff.py`

## Root Cause

`agent_tools.py` initializes `_workspace_root` to `None` and passes it directly to lower-level helpers:

```python
_workspace_root: Optional[str] = None
...
result = _read_file(..., workspace=_workspace_root)
...
result = _search_replace(..., workspace=_workspace_root)
```

The lower-level helpers only enforce containment if `workspace` is set:

```python
if workspace:
    if not is_path_within_directory(abs_path, workspace):
        return {"success": False, ...}
```

The already-hardened `write_file()` path uses `effective_workspace = workspace or os.getcwd()`. Current tests assert that `write_file(workspace=None)` must stay inside the current working directory. The same fail-closed default is missing from `read_file`, `search_replace`, `apply_diff`, and the agent wrappers that call them.

## Local-Only Reproduction

Run:

```bash
PYTHONPATH=/path/to/PraisonAI/src/praisonai:/path/to/PraisonAI/src/praisonai-agents \
  python poc_code_tools_workspace_bypass.py
```

Expected vulnerable result:

```text
[poc] HIT: CODE_TOOLS wrappers read and edit outside workspace when workspace is unset
```

The PoV creates a temporary workspace and a temporary file outside that workspace. With `get_workspace() == None`, `code_read_file()` reads the outside file, `code_search_replace()` modifies it, and `code_apply_diff()` modifies it again. After `set_workspace(workspace)`, the same outside path is rejected by all three wrappers.

No external services, model providers, or network access are used.

## Impact

If an application exposes PraisonAI Code's agent-compatible `CODE_TOOLS` to an LLM before setting a workspace boundary, prompt-influenced tool calls can read and modify files outside the intended project workspace. The practical attack shape matches the existing PraisonAI prompt-content advisory pattern: untrusted content influences an agent that has been given file-editing tools.

Practical impacts include:

- reading host secrets or local configuration files accessible to the process user;
- modifying arbitrary existing files when the attacker can supply or infer matching content for `code_search_replace` or `code_apply_diff`;
- using `code_read_file` to first learn file content and then `code_apply_diff` to produce an exact modification;
- bypassing the advertised workspace-boundary security posture unless the embedding application remembered to call `set_workspace()` first.

This issue does not claim `set_workspace()` is ineffective. The control works when configured. The vulnerability is the fail-open default for the advertised agent-tool bundle and adjacent read/edit helpers.

## Affected-Version Sweep

The same behavior was reproduced on:

- current upstream main: `2f9677abb2ea68eab864ee8b6a828fd0141612e1`
- `v4.6.57`
- `v4.6.56`
- `v4.6.10`
- `v4.6.9`
- `v4.5.128`
- `v4.5.126`
- `v3.9.26`
- `v3.9.24`

## Suggested Fix

Recommended fix:

1. Make every low-level file helper compute `effective_workspace = workspace or os.getcwd()` before resolving paths.
2. Make `code_read_file`, `code_list_files`, `code_apply_diff`, `code_search_replace`, and `code_execute_command` use `os.getcwd()` as the default workspace when `_workspace_root is None`.
3. Keep allowing absolute paths only when they resolve inside the effective workspace.
4. Add regression tests proving outside absolute paths are rejected before and after `set_workspace()`.
5. Consider failing closed if `CODE_TOOLS` is used before a workspace is configured, or log a warning when the default current working directory is used.

## Disclosure Route

PraisonAI's official security documentation lists GitHub Security Advisories as the preferred reporting method and asks reports to include reproduction steps, affected versions, impact, and suggested fixes. The repository security policy page currently shows no configured `SECURITY.md`, but private vulnerability reporting is available.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-gcq3-mfvh-3x25
- https://github.com/MervinPraison/PraisonAI
