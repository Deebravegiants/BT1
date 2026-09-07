# [H] phpMyAdmin PHP code injection

## Summary
Severity: High
Advisory: GHSA-wpww-hx7x-xfjh
CVE: CVE-2016-6609
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wpww-hx7x-xfjh
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin. A specially crafted database name could be used to run arbitrary PHP commands through the array export feature. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6609
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2018/07/msg00006.html
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-32
- http://www.securityfocus.com/bid/94112
