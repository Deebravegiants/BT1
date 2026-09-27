# [M] Incorrect authorization in the aggregation pipeline tool in Amazon AWS Labs DocumentDB MCP Server

## Summary
Severity: Medium
Advisory: CVE-2026-18954
Aliases: GHSA-j694-4m5j-w8hc
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-18954
Type: osv

## Details
Incorrect authorization in the aggregation pipeline tool in Amazon AWS Labs DocumentDB MCP Server before 1.0.12 might allow an authenticated MCP client to perform inappropriate write operations on the connected database via write-capable aggregation pipeline stages that bypass the read-only mode enforcement logic.



To remediate this issue, users should upgrade to version 1.0.12 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-076-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18954.json
- https://github.com/awslabs/mcp/security/advisories/GHSA-j694-4m5j-w8hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-18954
- https://github.com/awslabs/mcp/releases/tag/2026.04.20260408085348
