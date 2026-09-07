# [M] Microweber XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xmcr-x5x3-gjfx
CVE: CVE-2018-1000826
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xmcr-x5x3-gjfx
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.1

## Details
Microweber version <= 1.0.7 contains a Cross Site Scripting (XSS) vulnerability in Admin login form template that can result in Execution of JavaScript code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000826
- https://github.com/microweber/microweber/issues/489
- https://github.com/microweber/microweber/commit/5b29bc854bcfbfc5d4df1523ee221c900e7598a9
- https://0dd.zone/2018/10/28/microweber-XSS
- https://github.com/microweber/microweber
