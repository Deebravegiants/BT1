# [M] phpMyAdmin DoS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2mcj-3r3r-v5wm
CVE: CVE-2016-6623
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2mcj-3r3r-v5wm
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.0 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin. An authorized user can cause a denial-of-service (DoS) attack on a server by passing large values to a loop. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6623
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20210123204343/http://www.securityfocus.com/bid/95052
- https://www.phpmyadmin.net/security/PMASA-2016-46
