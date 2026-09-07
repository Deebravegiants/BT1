# [M] phpMyAdmin Implementation XSS Vulnerability on Server Monitor Page

## Summary
Severity: Medium
Advisory: GHSA-pvr5-84gr-g985
CVE: CVE-2014-8326
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pvr5-84gr-g985
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0.0 <4.0.10.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.1.0 <4.1.14.6
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.2.0 <4.2.10.1

## Details
Multiple cross-site scripting (XSS) vulnerabilities in phpMyAdmin 4.0.x before 4.0.10.5, 4.1.x before 4.1.14.6, and 4.2.x before 4.2.10.1 allow remote authenticated users to inject arbitrary web script or HTML via a crafted (1) database name or (2) table name, related to the `libraries/DatabaseInterface.class.php` code for SQL debug output and the `js/server_status_monitor.js` code for the server monitor page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8326
- https://github.com/phpmyadmin/phpmyadmin/commit/7b8962dede7631298c81e2c1cd267b81f1e08a8c
- https://github.com/phpmyadmin/phpmyadmin/commit/bd68c54d1beeef79d237e8bfda44690834012a76
- https://web.archive.org/web/20200228163625/http://www.securityfocus.com/bid/70731
- http://lists.opensuse.org/opensuse-updates/2014-11/msg00004.html
- http://www.phpmyadmin.net/home_page/security/PMASA-2014-12.php
