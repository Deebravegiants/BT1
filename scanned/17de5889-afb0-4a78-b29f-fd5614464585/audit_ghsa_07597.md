# [M] MCP Run Python Deno Sandbox Misconfiguration Allows SSRF Attacks via Localhost Access

## Summary
Severity: Medium
Advisory: GHSA-6fgp-m6q4-j3q5
CVE: CVE-2026-25904
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-6fgp-m6q4-j3q5
Type: github-advisory

## Affected
- PyPI: `mcp-run-python` — affected >=0

## Details
### Impact
**Server-Side Request Forgery (SSRF):**
A security vulnerability exists in the `mcp-run-python` tool (specifically within the Pydantic-AI integration) due to an overly permissive Deno sandbox configuration.

The tool configures the Deno runtime—which is intended to isolate the execution of untrusted Python code—with network permissions that include access to the host's loopback interface (`localhost`). Consequently, malicious Python code executed through the tool can bypass network isolation and send HTTP requests to internal services running on the host machine. This allows attackers to interact with local APIs, databases, or cloud metadata services that should not be accessible from the sandbox.

### Patches
**No Patch Available:**
The `mcp-run-python` project is currently **archived** and maintainers have indicated it is unlikely to receive a fix.

**Recommendation:**
Users are strongly advised to **immediately stop using** this package.
If functionality is required, users must migrate to an alternative execution environment that enforces strict network isolation (e.g., blocking all outbound traffic or explicitly denying access to `127.0.0.1`/`::1`).

### Workarounds
There are no configuration-based workarounds provided by the package itself. Remediation requires modifying the source code to restrict the Deno permissions (specifically removing or narrowing the `--allow-net` flag) or moving the execution to a container with no network access.

### Resources
* [CVE-2026-25904](https://nvd.nist.gov/vuln/detail/CVE-2026-25904)
* [JFrog Security Analysis: Deno SSRF](https://research.jfrog.com/vulnerabilities/mcp-run-python-deno-ssrf-jfsa-2026-001653029)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25904
- https://github.com/pydantic/mcp-run-python
- https://research.jfrog.com/vulnerabilities/mcp-run-python-deno-ssrf-jfsa-2026-001653029
