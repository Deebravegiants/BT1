# [H] @modelcontextprotocol/server-filesystem allows for path validation bypass via prefix matching and symlink handling

## Summary
Severity: High
Advisory: GHSA-q66q-fx2p-7w4m
CVE: CVE-2025-53109
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:N/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-07-01
Source: https://github.com/advisories/GHSA-q66q-fx2p-7w4m
Type: github-advisory

## Affected
- npm: `@modelcontextprotocol/server-filesystem` — affected >=0
- npm: `@modelcontextprotocol/server-filesystem` — affected >=2025.1.14 <2025.7.1

## Details
Versions of Filesystem prior to 0.6.3 & 2025.7.1 could allow access to unintended files via symlinks within allowed directories. Users are advised to upgrade to 2025.7.1 to resolve.

Thank you to Elad Beber (Cymulate) for reporting these issues.

## References
- https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-q66q-fx2p-7w4m
- https://nvd.nist.gov/vuln/detail/CVE-2025-53109
- https://github.com/modelcontextprotocol/servers/commit/d00c60df9d74dba8a3bb13113f8904407cda594f
- https://github.com/modelcontextprotocol/servers
