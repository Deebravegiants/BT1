# [M] Cross site scripting in automad/automad

## Summary
Severity: Medium
Advisory: GHSA-q3c8-65q7-9v78
CVE: CVE-2021-37502
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-03
Source: https://github.com/advisories/GHSA-q3c8-65q7-9v78
Type: github-advisory

## Affected
- Packagist: `automad/automad` — affected >=0 <1.8.0

## Details
Cross Site Scripting (XSS) vulnerability in automad 1.7.5 allows remote attackers to run arbitrary code via the user name field when adding a user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37502
- https://github.com/marcantondahmen/automad/issues/29
