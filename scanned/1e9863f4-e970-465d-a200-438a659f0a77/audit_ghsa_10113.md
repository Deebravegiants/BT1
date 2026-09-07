# [M] Apache Doris MCP Server vulnerable to SQL Injection via improper query context neutralization

## Summary
Severity: Medium
Advisory: GHSA-qhfq-gvvc-5q6q
CVE: CVE-2025-66335
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-qhfq-gvvc-5q6q
Type: github-advisory

## Affected
- PyPI: `doris-mcp-server` — affected >=0.1.0 <0.6.1

## Details
Apache Doris MCP Server versions prior to 0.6.1 are affected by an improper neutralization flaw in query context handling that may allow execution of unintended SQL statements and bypass of intended query validation and access restrictions through the MCP query execution interface. Versions 0.6.1 and later are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66335
- https://github.com/apache/doris-mcp-server
- https://github.com/apache/doris-mcp-server/releases/tag/0.6.1
- https://lists.apache.org/thread/odp0fyyst8kxm7hhm9z4d1snh1y4hjpy
- http://www.openwall.com/lists/oss-security/2026/04/17/4
