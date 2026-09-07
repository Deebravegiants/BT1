# [M] phpMyAdmin Local file exposure

## Summary
Severity: Medium
Advisory: GHSA-fcgm-62p3-f7cm
CVE: CVE-2016-6612
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fcgm-62p3-f7cm
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin. A user can exploit the LOAD LOCAL INFILE functionality to expose files on the server to the database system. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6612
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2019/06/msg00009.html
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-35
- http://www.securityfocus.com/bid/94113
