# [C] Code Injection in md-to-pdf.

## Summary
Severity: Critical
Advisory: GHSA-x949-7cm6-fm6p
CVE: CVE-2021-23639
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-x949-7cm6-fm6p
Type: github-advisory

## Affected
- npm: `md-to-pdf` — affected >=0 <5.0.0

## Details
The package md-to-pdf before 5.0.0 are vulnerable to Remote Code Execution (RCE) due to utilizing the library gray-matter to parse front matter content, without disabling the JS engine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23639
- https://github.com/simonhaenisch/md-to-pdf/issues/99
- https://github.com/simonhaenisch/md-to-pdf/commit/a716259c548c82fa1d3b14a3422e9100619d2d8a
- https://github.com/simonhaenisch/md-to-pdf
- https://snyk.io/vuln/SNYK-JS-MDTOPDF-1657880
