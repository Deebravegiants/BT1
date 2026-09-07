# [H] phpMyAdmin allows remote attackers to spoof content via the url parameter

## Summary
Severity: High
Advisory: GHSA-5pmg-qh2c-7j24
CVE: CVE-2015-7873
CWE: CWE-20, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5pmg-qh2c-7j24
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.0 <4.4.15.1
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.5.0 <4.5.1

## Details
The redirection feature in url.php in phpMyAdmin 4.4.x before 4.4.15.1 and 4.5.x before 4.5.1 allows remote attackers to spoof content via the url parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7873
- https://github.com/phpmyadmin/phpmyadmin/commit/2b31866fe0b30b867aaf5b5fedb11adb354e037f
- https://github.com/phpmyadmin/phpmyadmin/commit/cd097656758f981f80fb9029c7d6b4294582b706
- https://github.com/phpmyadmin/phpmyadmin
- https://web.archive.org/web/20161014120907/http://www.securitytracker.com/id/1034013
- https://web.archive.org/web/20200228052850/http://www.securityfocus.com/bid/77299
- https://www.phpmyadmin.net/security/PMASA-2015-5
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/171311.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/171326.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/169987.html
- http://www.debian.org/security/2015/dsa-3382
