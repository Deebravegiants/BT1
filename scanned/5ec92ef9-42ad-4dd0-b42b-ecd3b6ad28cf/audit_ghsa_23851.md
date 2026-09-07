# [M] phpMyAdmin Bypass logout timeout

## Summary
Severity: Medium
Advisory: GHSA-r2vw-p77f-vc27
CVE: CVE-2016-9851
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r2vw-p77f-vc27
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.9

## Details
An issue was discovered in phpMyAdmin. With a crafted request parameter value it is possible to bypass the logout timeout. All 4.6.x versions (prior to 4.6.5), and 4.4.x versions (prior to 4.4.15.9) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9851
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-62
- http://www.securityfocus.com/bid/94534
