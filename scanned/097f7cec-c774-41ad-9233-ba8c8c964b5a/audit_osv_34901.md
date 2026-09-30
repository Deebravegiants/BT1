# [H] Apache Doris MCP Server: SQL injection leading the authentication bypass

## Summary
Severity: High
Advisory: CVE-2025-66336
Aliases: GHSA-pqrj-4gwg-h5f7
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2025-66336
Type: osv

## Details
Apache Doris MCP Server contains a SQL injection vulnerability in a metadata query path. A user-controlled database name is directly interpolated into a SQL query, and the query is executed without passing the caller's authorization context. This may allow an authenticated attacker, or an anonymous attacker if authentication is disabled, to bypass SQL security validation and access metadata outside the intended database scope.

Affected users are recommended to upgrade to Doris version 0.6.1 or later, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/22/1
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66336.json
- https://lists.apache.org/thread/4l4v3m7ofwrgp4s4s98pjb5l03fcrzo2
- https://nvd.nist.gov/vuln/detail/CVE-2025-66336
