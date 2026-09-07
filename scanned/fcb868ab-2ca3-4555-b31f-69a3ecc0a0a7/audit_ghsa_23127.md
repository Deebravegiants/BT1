# [C] phpMyAdmin Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-567r-vqj7-5cw7
CVE: CVE-2016-6629
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-567r-vqj7-5cw7
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.17

## Details
An issue was discovered in phpMyAdmin involving the `$cfg['ArbitraryServerRegexp']` configuration directive. An attacker could reuse certain cookie values in a way of bypassing the servers defined by ArbitraryServerRegexp. All 4.6.x versions (prior to 4.6.4), 4.4.x versions (prior to 4.4.15.8), and 4.0.x versions (prior to 4.0.10.17) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6629
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20210725054025/http://www.securityfocus.com/bid/92493
- https://www.phpmyadmin.net/security/PMASA-2016-52
