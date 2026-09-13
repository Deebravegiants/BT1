# [H] MCP Python SDK has Unhandled Exception in Streamable HTTP Transport, Leading to Denial of Service

## Summary
Severity: High
Advisory: GHSA-j975-95f5-7wqh
CVE: CVE-2025-53365
CWE: CWE-248
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-04
Source: https://github.com/advisories/GHSA-j975-95f5-7wqh
Type: github-advisory

## Affected
- PyPI: `mcp` — affected >=0 <1.10.0

## Details
If a client deliberately triggers an exception after establishing a streamable HTTP session, this can lead to an uncaught ClosedResourceError on the server side, causing the server to crash and requiring a restart to restore service. Impact may vary depending on the deployment conditions, and presence of infrastructure-level resilience measures.

Thank you to Rich Harang for reporting this issue.

## References
- https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-j975-95f5-7wqh
- https://nvd.nist.gov/vuln/detail/CVE-2025-53365
- https://github.com/modelcontextprotocol/python-sdk/pull/967
- https://github.com/modelcontextprotocol/python-sdk/commit/7b420656de48cfdb90b39eb582e60b6d55c2f891
- https://github.com/advisories/GHSA-j975-95f5-7wqh
- https://github.com/modelcontextprotocol/python-sdk
- https://github.com/modelcontextprotocol/python-sdk/releases/tag/v1.10.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mcp/PYSEC-2026-1618.yaml
- https://pypi.org/project/mcp
