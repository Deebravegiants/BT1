# [C] PraisonAI: OS Command Injection in MCPHandler.parse_mcp_command()

## Summary
Severity: Critical
Advisory: GHSA-9gm9-c8mq-vq7m
CVE: CVE-2026-34935
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-9gm9-c8mq-vq7m
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=4.5.15 <4.5.69

## Details
### Summary

The `--mcp` CLI argument is passed directly to `shlex.split()` and forwarded through the call chain to `anyio.open_process()` with no validation, allowlist check, or sanitization at any hop, allowing arbitrary OS command execution as the process user.

### Details

`cli/features/mcp.py:61` (source) -> `praisonaiagents/mcp/mcp.py:345` (hop) -> `mcp/client/stdio/__init__.py:253` (sink)
```python
# source
parts = shlex.split(command)

# hop
cmd, args, env = self.parse_mcp_command(command, env_vars)
self.server_params = StdioServerParameters(command=cmd, args=arguments)

# sink
process = await anyio.open_process([command, *args])

```

Fixed in commit `47bff65413beaa3c21bf633c1fae4e684348368c` (v4.5.69) by introducing a command allowlist:
```python
ALLOWED_COMMANDS = {"npx", "uvx", "node", "python"}
if cmd not in ALLOWED_COMMANDS:
    raise ValueError(f"Disallowed command: {cmd}")
```

### PoC
```python
# tested on: praisonai==4.5.48
# install: pip install praisonai==4.5.48
# run: praisonai --mcp "bash -c 'id > /tmp/pwned'"
# verify: cat /tmp/pwned
# expected output: uid=1000(...) gid=1000(...) groups=1000(...)
```

### Impact

Any deployment where the `--mcp` argument is influenced by untrusted input is exposed to full OS command execution as the process user. No authentication is required.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-9gm9-c8mq-vq7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34935
- https://github.com/MervinPraison/PraisonAI/commit/47bff65413beaa3c21bf633c1fae4e684348368c
- https://github.com/MervinPraison/PraisonAI
