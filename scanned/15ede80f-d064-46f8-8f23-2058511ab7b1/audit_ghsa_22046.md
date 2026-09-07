# [C] phpMyAdmin SQL injection in Designer feature

## Summary
Severity: Critical
Advisory: GHSA-f732-fxh6-g4qj
CVE: CVE-2019-6798
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f732-fxh6-g4qj
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.8.5

## Details
An issue was discovered in phpMyAdmin before 4.8.5. A vulnerability was reported where a specially crafted username can be used to trigger a SQL injection attack through the designer feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6798
- https://github.com/phpmyadmin/composer
- https://www.phpmyadmin.net/security/PMASA-2019-2
- http://www.securityfocus.com/bid/106727
