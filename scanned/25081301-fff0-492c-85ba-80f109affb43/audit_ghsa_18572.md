# [H] @modelcontextprotocol/server-filesystem vulnerability allows for path validation bypass via colliding path prefix

## Summary
Severity: High
Advisory: GHSA-hc55-p739-j48w
CVE: CVE-2025-53110
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:N/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-07-01
Source: https://github.com/advisories/GHSA-hc55-p739-j48w
Type: github-advisory

## Affected
- npm: `@modelcontextprotocol/server-filesystem` — affected >=0
- npm: `@modelcontextprotocol/server-filesystem` — affected >=2025.1.14 <2025.7.1

## Details
Versions of Filesystem prior to 0.6.3 & 2025.7.1 could allow access to unintended files in cases where the prefix matches an allowed directory. Users are advised to upgrade to 2025.7.1 to resolve the issue.

Thank you to Elad Beber (Cymulate) for reporting these issues.

## References
- https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-hc55-p739-j48w
- https://nvd.nist.gov/vuln/detail/CVE-2025-53110
- https://github.com/modelcontextprotocol/servers/commit/cc99bdabdcad93a58877c5f3ab20e21d4394423d
- https://github.com/modelcontextprotocol/servers
