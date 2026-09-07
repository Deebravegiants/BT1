# [M] NodeBB Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vqr3-vrrg-f3jh
CVE: CVE-2024-57041
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-24
Source: https://github.com/advisories/GHSA-vqr3-vrrg-f3jh
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=0 <3.11.1

## Details
A persistent cross-site scripting (XSS) vulnerability in NodeBB v3.11.0 allows remote attackers to store arbitrary code in the 'about me' section of their profile.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57041
- https://github.com/NodeBB/NodeBB/commit/4e69bff72fd04779064d37e46a43080e6c328adf
- https://github.com/NodeBB/NodeBB
- https://www.tonysec.com/posts/cve-2024-57041
