# [M] phpMyAdmin IPv6 and proxy server IP-based authentication rule circumvention

## Summary
Severity: Medium
Advisory: GHSA-mhxj-6vf8-mwv3
CVE: CVE-2016-6624
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mhxj-6vf8-mwv3
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin involving improper enforcement of the IP-based authentication rules. When phpMyAdmin is used with IPv6 in a proxy server environment, and the proxy server is in the allowed range but the attacking computer is not allowed, this vulnerability can allow the attacking computer to connect despite the IP rules. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6624
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2019/06/msg00009.html
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-47
- http://www.securityfocus.com/bid/92489
