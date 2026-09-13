# [C] MCP-for-Stata: Command injection via log_file_name parameter in Stata command wrapper

## Summary
Severity: Critical
Advisory: GHSA-4p62-hqp5-g644
CVE: CVE-2026-47708
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-4p62-hqp5-g644
Type: github-advisory

## Affected
- PyPI: `stata-mcp` — affected >=0 <1.17.3

## Details
### Summary
The `log_file_name` parameter in the `stata_do` API and CLI is directly interpolated into a Stata command string without sanitization. The security guard (`GuardValidator`) only scans the do-file content but does not validate this parameter. An attacker can inject arbitrary Stata commands (including `shell`, `python`, `erase`, etc.) by crafting a malicious `log_file_name` containing quotes, newlines, or Stata command separators.

### Details

In `src/stata_mcp/stata/stata_do/do.py`, both `_execute_unix_like` and `_execute_windows` construct a Stata command string using Python f-strings:

```python
commands = f"""
capture log close
{self.generate_log_command(log_file, is_replace)}
...
do "{dofile_path}"
...
"""
```

The `generate_log_command` method returns:

```python
log_cmd = f'log using "{log_file.as_posix()}", {replace_clause} {log_type} name({log_type}_log)'
```

Where `log_file` is constructed from user-supplied `log_name`:

```python
def generate_log_file(self, log_name: str, extension='log'):
    return self.log_file_path / f"{log_name}.{extension}"
```

The `log_name` parameter comes directly from user input (via MCP tool `stata_do` or CLI `stata-mcp tool do`) without any validation. Since the path is embedded inside double quotes in a Stata command string, an attacker can break out of the string context and inject arbitrary commands.

Additionally, `generate_log_file` does not prevent path traversal via `log_name`, allowing arbitrary file write outside the intended log directory.

### Proof of Concept

When calling `stata_do` via MCP tool with:

```json
{
  "dofile_path": "test.do",
  "log_file_name": "'; shell echo pwned > /tmp/pwned.txt; '"
}
```

The generated Stata commands become:

```stata
log using "<log_dir>/'; shell echo pwned > /tmp/pwned.txt; '.log", replace text name(text_log)
```

Stata interprets this as multiple commands, with `shell echo pwned > /tmp/pwned.txt;` executed as an arbitrary shell command.

### Impact

- **Remote Code Execution** via `shell` command injection
- **Arbitrary file write/overwrite** via path traversal in `log_name`
- Complete bypass of the security guard, as the guard only validates do-file content, not wrapper parameters

### Remediation / Fix

1. Apply strict allowlist validation to `log_name` (only alphanumeric, underscore, dot, hyphen; max 128 chars)
2. Resolve and verify the constructed log path remains within the intended log directory
3. Consider generating safe internal filenames (e.g., UUIDs) instead of accepting user-defined log names for command construction
4. Apply similar sanitization to `dofile_path` before embedding it into Stata command strings

### References

- Issue: #74
- Fix commit: https://github.com/SepineTam/stata-mcp/commit/e6f945941ae0c7cf5e74a428e0b3dc82b396382f

## References
- https://github.com/SepineTam/stata-mcp/security/advisories/GHSA-4p62-hqp5-g644
- https://github.com/SepineTam/mcp-for-stata/issues/74
- https://github.com/SepineTam/mcp-for-stata/commit/e6f945941ae0c7cf5e74a428e0b3dc82b396382f
- https://github.com/SepineTam/stata-mcp
