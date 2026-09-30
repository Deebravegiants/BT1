# [M] Apache Doris-MCP-Server: Improper Access Control results in bypassing a "read-only" mode

## Summary
Severity: Medium
Advisory: GHSA-m35w-xx8c-6xc7
CVE: CVE-2025-58337
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-05
Source: https://github.com/advisories/GHSA-m35w-xx8c-6xc7
Type: github-advisory

## Affected
- PyPI: `doris-mcp-server` — affected >=0 <0.6.0

## Details
An attacker with a valid read-only account can bypass Doris MCP Server’s read-only mode due to improper access control, allowing modifications that should have been prevented by read-only restrictions.

Impact:

Bypasses read-only mode; attackers with read-only access may perform unauthorized modifications.

Recommended action for operators: Upgrade to version 0.6.0 as soon as possible (this release contains the fix).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-58337
- https://github.com/apache/doris-mcp-server/commit/5923cc1c8973069a6d54eca1948a10488cbf409e
- https://github.com/apache/doris-mcp-server
- https://lists.apache.org/thread/6tswlphj0pqn9zf25594r3c1vzvfj40h
- https://security.snyk.io/vuln/SNYK-PYTHON-DORISMCPSERVER-13835132
- http://www.openwall.com/lists/oss-security/2025/11/04/5
