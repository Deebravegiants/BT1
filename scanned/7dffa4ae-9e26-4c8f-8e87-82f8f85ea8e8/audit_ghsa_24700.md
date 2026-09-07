# [M] phpMyAdmin Reflected File Download attack

## Summary
Severity: Medium
Advisory: GHSA-phhm-63xx-v9rr
CVE: CVE-2016-6628
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-phhm-63xx-v9rr
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin. An attacker may be able to trigger a user to download a specially crafted malicious SVG file. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6628
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2019/06/msg00009.html
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-51
- http://www.securityfocus.com/bid/92492
