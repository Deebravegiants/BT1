# [H] phpMyAdmin SSRF in replication

## Summary
Severity: High
Advisory: GHSA-99xj-xqc9-98hr
CVE: CVE-2017-1000017
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-99xj-xqc9-98hr
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.6
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.10
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.19

## Details
phpMyAdmin 4.0, 4.4 and 4.6 are vulnerable to a weakness where a user with appropriate permissions is able to connect to an arbitrary MySQL server

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000017
- https://github.com/phpmyadmin/composer
- https://www.phpmyadmin.net/security/PMASA-2017-6
- http://www.securityfocus.com/bid/95732
