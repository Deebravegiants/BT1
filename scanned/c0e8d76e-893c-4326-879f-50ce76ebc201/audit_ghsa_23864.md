# [H] phpMyAdmin CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-xwf2-53mc-r8hx
CVE: CVE-2018-19969
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xwf2-53mc-r8hx
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.8 <4.8.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.7

## Details
phpMyAdmin 4.7.x and 4.8.x versions prior to 4.8.4 are affected by a series of CSRF flaws. By deceiving a user into clicking on a crafted URL, it is possible to perform harmful SQL operations such as renaming databases, creating new tables/routines, deleting designer pages, adding/deleting users, updating user passwords, killing SQL processes, etc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19969
- https://security.gentoo.org/glsa/201904-16
- https://web.archive.org/web/20210124223800/https://www.securityfocus.com/bid/106175
- https://www.phpmyadmin.net/security/PMASA-2018-7
