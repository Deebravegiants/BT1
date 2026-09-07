# [H] phpMyAdmin SQL injection in user accounts page

## Summary
Severity: High
Advisory: GHSA-fgj8-93xx-f6g6
CVE: CVE-2020-5504
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fgj8-93xx-f6g6
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0.0 <4.9.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=5.0.0 <5.0.1

## Details
In phpMyAdmin 4 before 4.9.4 and 5 before 5.0.1, SQL injection exists in the user accounts page. A malicious user could inject custom SQL in place of their own username when creating queries to this page. An attacker must have a valid MySQL account to access the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5504
- https://cybersecurityworks.com/zerodays/cve-2020-5504-phpmyadmin.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmyadmin/phpmyadmin/CVE-2020-5504.yaml
- https://github.com/MarkLee131/awesome-web-pocs/blob/main/CVE-2020-5504.md
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2020/01/msg00011.html
- https://www.phpmyadmin.net/security/PMASA-2020-1
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00024.html
