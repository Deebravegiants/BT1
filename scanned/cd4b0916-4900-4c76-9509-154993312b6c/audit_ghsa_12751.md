# [M] Joplin Desktop App vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-h6c2-879r-jffh
CVE: CVE-2022-45598
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-h6c2-879r-jffh
Type: github-advisory

## Affected
- npm: `joplin` — affected >=0 <2.9.17

## Details
Cross Site Scripting vulnerability in Joplin Desktop App before v2.9.17 allows attacker to execute arbitrary code via improper santization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45598
- https://github.com/laurent22/joplin/commit/a2de167b95debad83a0f0c7925a88c0198db812e
- https://github.com/laurent22/joplin
- https://github.com/laurent22/joplin/releases/tag/v2.9.17
