# [M] Joplin Cross Site Scripting Vulnerability via NOSCRIPT tags

## Summary
Severity: Medium
Advisory: GHSA-phj8-2p6x-hq5r
CVE: CVE-2021-33295
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-phj8-2p6x-hq5r
Type: github-advisory

## Affected
- npm: `joplin` — affected >=0 <1.8.5

## Details
Cross Site Scripting (XSS) vulnerability in Joplin Desktop App before 1.8.5 allows attackers to execute aribrary code due to improper sanitizing of html.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33295
- https://github.com/laurent22/joplin/commit/9c20d5947d1fa4678a8b640792ff3d31224f0adf
- https://github.com/laurent22/joplin
- https://github.com/laurent22/joplin/releases/tag/v1.8.5
- https://the-it-wonders.blogspot.com/2021/05/joplin-app-desktop-version-vulnerable.html
