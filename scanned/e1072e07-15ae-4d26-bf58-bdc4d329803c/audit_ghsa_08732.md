# [C] Open Source Kubectl MCP Server vulnerable to arbitrary code execution via user interaction with crafted HTML page

## Summary
Severity: Critical
Advisory: GHSA-94gr-w3q5-rfqr
CVE: CVE-2025-65719
CWE: CWE-94
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-94gr-w3q5-rfqr
Type: github-advisory

## Affected
- npm: `kubectl-mcp-server` — affected >=0 <1.2.0
- PyPI: `kubectl-mcp-server` — affected >=0 <1.2.0

## Details
An issue in Open Source Kubectl MCP Server v1.1.1 allows attackers to execute arbitrary code on a victim system via user interaction with a crafted HTML page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65719
- https://github.com/rohitg00/kubectl-mcp-server
- https://www.ox.security/blog/cve-2025-65719-critical-rce-in-kubectl-mcp-server
- https://www.ox.security/blog/kubectl-mcp-server-remote-code-execution
