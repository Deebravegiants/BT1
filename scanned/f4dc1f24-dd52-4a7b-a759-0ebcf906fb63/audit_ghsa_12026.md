# [M] FastMCP has a Command Injection vulnerability - Gemini CLI

## Summary
Severity: Medium
Advisory: GHSA-m8x7-r2rg-vh5g
CVE: CVE-2025-64340
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-m8x7-r2rg-vh5g
Type: github-advisory

## Affected
- PyPI: `fastmcp` — affected >=0 <3.2.0

## Details
Server names containing shell metacharacters (e.g., `&`) can cause command injection on Windows when passed to `fastmcp install claude-code` or `fastmcp install gemini-cli`. These install paths use `subprocess.run()` with a list argument, but on Windows the target CLIs often resolve to `.cmd` wrappers that are executed through `cmd.exe`, which interprets metacharacters in the flattened command string.

PoC:
```python
from fastmcp import FastMCP

mcp = FastMCP(name="test&calc")

@mcp.tool
def roll_dice(n_dice: int) -> list[int]:
    """Roll `n_dice` 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]
```

```
fastmcp install claude-code server.py   # or: fastmcp install gemini-cli server.py
```

On Windows, this opens Calculator via the `&calc` in the server name.

Impact:
Arbitrary command execution with the privileges of the user running `fastmcp install`. Affects Windows hosts where the target CLI (one of claude, gemini) is installed as a `.cmd` wrapper. Does not affect macOS/Linux, and does not affect config-file-based install targets (cursor, goose, mcp-json).

Patched in #3522 by validating server names to reject shell metacharacters.

## References
- https://github.com/PrefectHQ/fastmcp/security/advisories/GHSA-m8x7-r2rg-vh5g
- https://github.com/jlowin/fastmcp/security/advisories/GHSA-m8x7-r2rg-vh5g
- https://nvd.nist.gov/vuln/detail/CVE-2025-64340
- https://github.com/PrefectHQ/fastmcp/pull/3522
- https://github.com/PrefectHQ/fastmcp
