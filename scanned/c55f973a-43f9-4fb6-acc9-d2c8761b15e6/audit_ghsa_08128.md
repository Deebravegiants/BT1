# [M] MCP Run Python has a Sandbox Escape & Server Takeover Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pfv4-wmph-5gc6
CVE: CVE-2026-25905
CWE: CWE-653
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-pfv4-wmph-5gc6
Type: github-advisory

## Affected
- PyPI: `mcp-run-python` — affected >=0

## Details
### Impact
**Critical Sandbox Escape & Server Takeover:**
A critical security vulnerability exists in `mcp-run-python` due to a lack of isolation between the Python runtime (Pyodide) and the host JavaScript environment.

The `runPython` and `runPythonAsync` functions execute Python code using Pyodide without restricting access to the JavaScript bridge. This allows any executed Python code—whether from a user or an AI model—to access the `js` module in Pyodide. Through this bridge, the Python code can modify the global JavaScript environment, interact with the Node.js process, and alter the behavior of the MCP server.

**Specific Attack Vector: MCP Tool Shadowing**
Because the Python code can modify the JS runtime, an attacker can dynamically overwrite or "shadow" existing MCP tools registered on the server. For example, an attacker could replace a secure file-reading tool with a malicious version that exfiltrates data to an external server, all while the MCP server appears to be functioning normally.

### Patches
**No Patch Available:**
The `mcp-run-python` project is currently **archived** and maintainers have indicated it is unlikely to receive a fix.

**Recommendation:**
Users are strongly advised to **immediately stop using** this package.
If functionality is required, users must migrate to a maintained alternative that implements proper sandboxing (e.g., running Python in a Docker container or a restricted WASM environment with the JS bridge disabled).

### Workarounds
There are no configuration-based workarounds. Securing the environment requires modifying the source code to disable the Pyodide-to-JS bridge or moving the execution environment to a fully isolated sandbox (e.g., a separate container).

### Resources
* [CVE-2026-25905](https://nvd.nist.gov/vuln/detail/CVE-2026-25905)
* [JFrog Security Analysis: MCP Takeover](https://research.jfrog.com/vulnerabilities/mcp-run-python-lack-of-isolation-mcp-takeover-jfsa-2026-001653030)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25905
- https://github.com/pydantic/mcp-run-python
- https://research.jfrog.com/vulnerabilities/mcp-run-python-lack-of-isolation-mcp-takeover-jfsa-2026-001653030
