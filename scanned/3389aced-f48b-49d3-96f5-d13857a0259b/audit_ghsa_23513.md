# [H] phpMyAdmin DoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-qgrq-64g6-mmh6
CVE: CVE-2016-9863
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qgrq-64g6-mmh6
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.5

## Details
An issue was discovered in phpMyAdmin. With a very large request to table partitioning function, it is possible to invoke a Denial of Service (DoS) attack. All 4.6.x versions (prior to 4.6.5) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9863
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20210123194704/http://www.securityfocus.com/bid/94526
- https://www.phpmyadmin.net/security/PMASA-2016-68
