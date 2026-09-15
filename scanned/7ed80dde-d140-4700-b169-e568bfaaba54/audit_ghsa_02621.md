# [C] SQL Injection in topthink/thinkphp

## Summary
Severity: Critical
Advisory: GHSA-m7h5-fjjq-559f
CVE: CVE-2020-20120
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-30
Source: https://github.com/advisories/GHSA-m7h5-fjjq-559f
Type: github-advisory

## Affected
- Packagist: `topthink/thinkphp` — affected >=0

## Details
ThinkPHP v3.2.3 and below contains a SQL injection vulnerability which is triggered when the array is not passed to the "where" and "query" methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-20120
- https://github.com/top-think/thinkphp/issues/553
- https://github.com/top-think/thinkphp
