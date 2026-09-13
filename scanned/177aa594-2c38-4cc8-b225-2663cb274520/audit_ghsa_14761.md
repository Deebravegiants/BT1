# [M] Oqtane Framework Insecure Direct Object Reference vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hhcw-wwxv-g95c
CVE: CVE-2024-55471
CWE: CWE-639
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-20
Source: https://github.com/advisories/GHSA-hhcw-wwxv-g95c
Type: github-advisory

## Affected
- NuGet: `Oqtane.Framework` — affected >=0
- NuGet: `Oqtane.Server` — affected >=0

## Details
Oqtane Framework is vulnerable to Insecure Direct Object Reference (IDOR) in Oqtane.Controllers.UserController. This allows unauthorized users to access sensitive information of other users by manipulating the id parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55471
- https://github.com/oqtane/oqtane.framework/pull/4880/files
- https://github.com/oqtane/oqtane.framework
- https://medium.com/@Rudra_2158/cve-2024-55471-breaking-down-the-idor-vulnerability-in-oqtane-framework-c0f4b02f12fc
