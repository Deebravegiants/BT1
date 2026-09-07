# [H] phpMyAdmin Cookie attribute injection attack

## Summary
Severity: High
Advisory: GHSA-j2cq-h6v2-f875
CVE: CVE-2017-1000016
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j2cq-h6v2-f875
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.6

## Details
A weakness was discovered where an attacker can inject arbitrary values in to the browser cookies. This is a re-issue of an incomplete fix from PMASA-2016-18.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000016
- https://github.com/phpmyadmin/phpmyadmin/commit/3b6ed1f
- https://www.phpmyadmin.net/security/PMASA-2017-5
