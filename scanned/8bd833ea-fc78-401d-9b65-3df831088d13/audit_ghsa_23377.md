# [M] phpMyAdmin DoS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qf3f-7x69-qfv3
CVE: CVE-2016-6622
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qf3f-7x69-qfv3
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin. An unauthenticated user is able to execute a denial-of-service (DoS) attack by forcing persistent connections when phpMyAdmin is running with `$cfg['AllowArbitraryServer']=true`. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6622
- https://lists.debian.org/debian-lts-announce/2018/07/msg00006.html
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20210125183746/http://www.securityfocus.com/bid/95049
- https://www.phpmyadmin.net/security/PMASA-2016-45
