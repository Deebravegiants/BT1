# [H] MCP Python SDK vulnerability in the FastMCP Server causes validation error, leading to DoS

## Summary
Severity: High
Advisory: GHSA-3qhf-m339-9g5v
CVE: CVE-2025-53366
CWE: CWE-248
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-04
Source: https://github.com/advisories/GHSA-3qhf-m339-9g5v
Type: github-advisory

## Affected
- PyPI: `mcp` — affected >=0 <1.9.4

## Details
A validation error in the MCP SDK can cause an unhandled exception when processing malformed requests, resulting in service unavailability (500 errors) until manually restarted. Impact may vary depending on the deployment conditions, and presence of infrastructure-level resilience measures.

Thank you to Rich Harang for reporting this issue.

## References
- https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-3qhf-m339-9g5v
- https://nvd.nist.gov/vuln/detail/CVE-2025-53366
- https://github.com/modelcontextprotocol/python-sdk/pull/822
- https://github.com/modelcontextprotocol/python-sdk/commit/29c69e6a47d0104d0afcea6ac35e7ab02fde809a
- https://github.com/advisories/GHSA-3qhf-m339-9g5v
- https://github.com/modelcontextprotocol/python-sdk
- https://github.com/modelcontextprotocol/python-sdk/releases/tag/v1.9.4
- https://github.com/pypa/advisory-database/tree/main/vulns/mcp/PYSEC-2026-1616.yaml
- https://pypi.org/project/mcp
