# [H] phpMyAdmin vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-2p7v-jm8m-g3qq
CVE: CVE-2016-5739
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2p7v-jm8m-g3qq
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0.10.0 <4.0.10.16
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.15.0 <4.4.15.7
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.3

## Details
The Transformation implementation in phpMyAdmin 4.0.x before 4.0.10.16, 4.4.x before 4.4.15.7, and 4.6.x before 4.6.3 does not use the no-referrer Content Security Policy (CSP) protection mechanism, which makes it easier for remote attackers to conduct CSRF attacks by reading an authentication token in a Referer header, related to libraries/Header.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5739
- https://github.com/phpmyadmin/phpmyadmin/commit/1e5716cb96d46efc305381ae0da08e73fe340f05
- https://github.com/phpmyadmin/phpmyadmin/commit/2f4950828ec241e8cbdcf13090c2582a6fa620cb
- https://github.com/phpmyadmin/phpmyadmin
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20200227223419/http://www.securityfocus.com/bid/91389
- https://www.phpmyadmin.net/security/PMASA-2016-28
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00113.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00114.html
- http://www.debian.org/security/2016/dsa-3627
