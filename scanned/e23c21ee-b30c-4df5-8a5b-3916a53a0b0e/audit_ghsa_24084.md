# [M] Cross site scripting in Croogo

## Summary
Severity: Medium
Advisory: GHSA-r4h9-gv2m-9x97
CVE: CVE-2017-1000510
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r4h9-gv2m-9x97
Type: github-advisory

## Affected
- Packagist: `croogo/croogo` — affected >=0 <4.0.0

## Details
Croogo versions before 4.x contain a Cross Site Scripting (XSS) vulnerability in Page name that can result in execution of javascript code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000510
- https://github.com/croogo/croogo/issues/847
