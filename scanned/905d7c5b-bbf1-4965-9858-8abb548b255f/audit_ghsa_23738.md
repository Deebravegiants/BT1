# [H] phpMyAdmin DoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-47qr-f86f-3wm4
CVE: CVE-2017-1000018
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-47qr-f86f-3wm4
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.6
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.10
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.19

## Details
phpMyAdmin 4.0, 4.4., and 4.6 are vulnerable to a DOS attack in the replication status by using a specially crafted table name

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000018
- https://web.archive.org/web/20210123220317/http://www.securityfocus.com/bid/95738
- https://www.phpmyadmin.net/security/PMASA-2017-7
