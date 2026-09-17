# [C] npos-tesseract Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-mpwp-pf96-9g4r
CVE: CVE-2020-28453
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-03
Source: https://github.com/advisories/GHSA-mpwp-pf96-9g4r
Type: github-advisory

## Affected
- npm: `npos-tesseract` — affected >=0

## Details
A command injection vulnerability affects all versions of package npos-tesseract. The injection point is located in line 55 in lib/ocr.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28453
- https://github.com/taoyuan/npos-tesseract
- https://security.snyk.io/vuln/SNYK-JS-NPOSTESSERACT-1051031
