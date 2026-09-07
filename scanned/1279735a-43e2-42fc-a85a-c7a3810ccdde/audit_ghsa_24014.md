# [M] phpMyAdmin allows to detect if user is logged in

## Summary
Severity: Medium
Advisory: GHSA-r643-7xfg-ppc5
CVE: CVE-2016-6625
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r643-7xfg-ppc5
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin. An attacker can determine whether a user is logged in to phpMyAdmin. The user's session, username, and password are not compromised by this vulnerability. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6625
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-48
- http://www.securityfocus.com/bid/92491
