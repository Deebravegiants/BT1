# [C] phpMyAdmin Improper Privilege Management

## Summary
Severity: Critical
Advisory: GHSA-5868-g58j-vrj5
CVE: CVE-2017-18264
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5868-g58j-vrj5
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.20
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.7.0-beta1 <4.7.0
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.0
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0

## Details
An issue was discovered in libraries/common.inc.php in phpMyAdmin 4.0 before 4.0.10.20, 4.4.x, 4.6.x, and 4.7.0 prereleases. The restrictions caused by $cfg['Servers'][$i]['AllowNoPassword'] = false are bypassed under certain PHP versions (e.g., version 5). This can allow the login of users who have no password set even if the administrator has set $cfg['Servers'][$i]['AllowNoPassword'] to false (which is also the default). This occurs because some implementations of the PHP substr function return false when given '' as the first argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18264
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2018/07/msg00006.html
- https://www.phpmyadmin.net/security/PMASA-2017-8
- http://www.securityfocus.com/bid/97211
