# [M] Simditor XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p9wj-wrrm-84m5
CVE: CVE-2018-6464
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p9wj-wrrm-84m5
Type: github-advisory

## Affected
- npm: `simditor` — affected >=0

## Details
Simditor v2.3.11 allows XSS via crafted use of `svg/onload=alert` in a TEXTAREA element, as demonstrated by Firefox 54.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6464
- https://github.com/Heartway/simditor
- https://github.com/Heartway/simditor/blob/master/simditor.docx
