# [H] phpMyAdmin Bypass white-list protection for URL redirection

## Summary
Severity: High
Advisory: GHSA-r326-mp8g-6xfc
CVE: CVE-2016-9861
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r326-mp8g-6xfc
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.9
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.18

## Details
An issue was discovered in phpMyAdmin. Due to the limitation in URL matching, it was possible to bypass the URL white-list protection. All 4.6.x versions (prior to 4.6.5), 4.4.x versions (prior to 4.4.15.9), and 4.0.x versions (prior to 4.0.10.18) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9861
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2019/06/msg00009.html
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-66
- http://www.securityfocus.com/bid/94535
