# [M] OpenCart SQL injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-236j-rfx5-wq38
CVE: CVE-2021-37823
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-03
Source: https://github.com/advisories/GHSA-236j-rfx5-wq38
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=0

## Details
OpenCart 3.0.3.7 allows users to obtain database information or read server files through SQL injection in the background.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37823
- https://github.com/opencart/opencart
- https://medium.com/@nowczj/sql-injection-exists-in-the-background-of-opencart-d41b5c58e99e
