# [M] phpMyAdmin XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pw34-qf6c-84fc
CVE: CVE-2016-2040
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pw34-qf6c-84fc
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.13
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.3
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.5 <4.5.4

## Details
Multiple cross-site scripting (XSS) vulnerabilities in phpMyAdmin 4.0.x before 4.0.10.13, 4.4.x before 4.4.15.3, and 4.5.x before 4.5.4 allow remote authenticated users to inject arbitrary web script or HTML via a (1) table name, (2) SET value, (3) search query, or (4) hostname in a Location header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2040
- https://github.com/phpmyadmin/phpmyadmin/commit/75a55824012406a08c4debf5ddb7ae41c32a7dbc
- https://github.com/phpmyadmin/phpmyadmin/commit/aca42efa01917cc0fe8cfdb2927a6399ca1742f2
- https://github.com/phpmyadmin/phpmyadmin/commit/edffb52884b09562490081c3b8666ef46c296418
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176483.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176739.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00028.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00049.html
- http://www.debian.org/security/2016/dsa-3627
- http://www.phpmyadmin.net/home_page/security/PMASA-2016-3.php
