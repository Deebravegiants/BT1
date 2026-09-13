# [H] Apache SkyWalking MCP: Server-Side Request Forgery via SW-URL Header in MCP Server

## Summary
Severity: High
Advisory: GHSA-c4hg-6933-x62x
CVE: CVE-2026-34476
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-c4hg-6933-x62x
Type: github-advisory

## Affected
- Go: `github.com/apache/skywalking-mcp` — affected >=0 <0.2.0

## Details
Server-Side Request Forgery via SW-URL Header vulnerability in Apache SkyWalking MCP.

This issue affects Apache SkyWalking MCP: 0.1.0.

Users are recommended to upgrade to version 0.2.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34476
- https://github.com/advisories/GHSA-c4hg-6933-x62x
- https://github.com/apache/skywalking-mcp
- https://lists.apache.org/thread/v0k1xyzzbtnpyrwxwyn36pbspr8rhjnr
- http://www.openwall.com/lists/oss-security/2026/04/13/4
