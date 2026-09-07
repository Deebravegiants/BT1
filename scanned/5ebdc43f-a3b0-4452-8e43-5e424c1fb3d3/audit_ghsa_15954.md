# [M] Glossarizer Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hhhv-ggjx-q9j2
CVE: CVE-2024-42515
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-hhhv-ggjx-q9j2
Type: github-advisory

## Affected
- npm: `glossarizer` — affected >=0

## Details
Glossarizer through 1.5.2 improperly tries to convert text into HTML. Even though the application itself escapes special characters (e.g., <>), the underlying library converts these encoded characters into legitimate HTML, thereby possibly causing stored XSS. Attackers can append a XSS payload to a word that has a corresponding glossary entry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42515
- https://github.com/PebbleRoad/glossarizer
- https://herolab.usd.de/security-advisories/usd-2024-0011
- https://www.npmjs.com/package/glossarizer
