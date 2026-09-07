# [H] phpMyAdmin Cryptographic Vulnerability

## Summary
Severity: High
Advisory: GHSA-4gmg-gwjh-3mmr
CVE: CVE-2016-1927
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4gmg-gwjh-3mmr
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0.0 <4.0.10.13
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.0 <4.4.15.3
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.5.0 <4.5.4

## Details
The `suggestPassword` function in `js/functions.js` in phpMyAdmin 4.0.x before 4.0.10.13, 4.4.x before 4.4.15.3, and 4.5.x before 4.5.4 relies on the `Math.random` JavaScript function, which makes it easier for remote attackers to guess passwords via a brute-force approach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1927
- https://github.com/phpmyadmin/phpmyadmin/commit/2369daa7f5f550797f560e6b46a021e4558c2d72
- https://github.com/phpmyadmin/phpmyadmin/commit/5530a72e162fab442218486a90ff3365c96fde98
- https://github.com/phpmyadmin/phpmyadmin/commit/6a96e67487f2faecb4de4204fee9b96b94020720
- https://github.com/phpmyadmin/phpmyadmin/commit/8b6737735be5787d0b98c6cdfe2c7e3131b1bc95
- https://github.com/phpmyadmin/phpmyadmin/commit/8dedcc1a175eb07debd4fe116407c43694c60b22
- https://github.com/phpmyadmin/phpmyadmin/commit/912856b432d794201884c36e5f390d446339b6e4
- https://github.com/phpmyadmin/phpmyadmin
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176483.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176739.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00028.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00049.html
- http://www.debian.org/security/2016/dsa-3627
- http://www.phpmyadmin.net/home_page/security/PMASA-2016-4.php
