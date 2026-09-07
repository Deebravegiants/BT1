# [M] x-data-spreadsheet through 1.1.9 vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-x5cw-843f-r366
CVE: CVE-2022-25646
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-31
Source: https://github.com/advisories/GHSA-x5cw-843f-r366
Type: github-advisory

## Affected
- npm: `x-data-spreadsheet` — affected >=0

## Details
All versions of package x-data-spreadsheet are vulnerable to Cross-site Scripting (XSS) due to missing sanitization of values inserted into the cells.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25646
- https://github.com/myliang/x-spreadsheet/issues/580
- https://github.com/myliang/x-spreadsheet
- https://security.snyk.io/vuln/SNYK-JS-XDATASPREADSHEET-2430381
- https://youtu.be/Ij-8VVKNh7U
