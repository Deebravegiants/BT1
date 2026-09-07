# [M] Cross-site Scripting in GilaCMS

## Summary
Severity: Medium
Advisory: GHSA-h7mq-27r7-w972
CVE: CVE-2020-20696
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-30
Source: https://github.com/advisories/GHSA-h7mq-27r7-w972
Type: github-advisory

## Affected
- Packagist: `gilacms/gila` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in /admin/content/post of GilaCMS v1.11.4 allows attackers to execute arbitrary web scripts or HTML via a crafted payload in the Tags field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-20696
- https://github.com/GilaCMS/gila/issues/53
- https://github.com/GilaCMS/gila
