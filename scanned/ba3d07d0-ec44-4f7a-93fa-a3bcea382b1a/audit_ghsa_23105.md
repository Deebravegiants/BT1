# [C] phpMyAdmin unsanitized Git information

## Summary
Severity: Critical
Advisory: GHSA-pgph-mc4p-f8c3
CVE: CVE-2019-19617
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pgph-mc4p-f8c3
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.9.2

## Details
phpMyAdmin before 4.9.2 does not escape certain Git information, related to `libraries/classes/Display/GitRevision.php and libraries/classes/Footer.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19617
- https://github.com/phpmyadmin/phpmyadmin/commit/1119de642b136d20e810bb20f545069a01dd7cc9
- https://github.com/phpmyadmin/composer
- https://github.com/phpmyadmin/phpmyadmin/compare/RELEASE_4_9_1...RELEASE_4_9_2
- https://lists.debian.org/debian-lts-announce/2019/12/msg00006.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00024.html
- https://www.phpmyadmin.net/news/2019/11/22/phpmyadmin-492-released
