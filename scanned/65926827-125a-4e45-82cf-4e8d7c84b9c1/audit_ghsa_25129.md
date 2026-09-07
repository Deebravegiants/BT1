# [M] phpMyAdmin Global variables scope injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x962-w72p-mv7q
CVE: CVE-2013-4729
CWE: CWE-621
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-x962-w72p-mv7q
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.4.1

## Details
import.php in phpMyAdmin 4.x before 4.0.4.1 does not properly restrict the ability of input data to specify a file format, which allows remote authenticated users to modify the GLOBALS superglobal array, and consequently change the configuration, via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4729
- https://github.com/phpmyadmin/phpmyadmin/commit/012464268420e53a9cd81cbb4a43988d70393c36
- https://github.com/phpmyadmin/phpmyadmin
- http://www.phpmyadmin.net/home_page/security/PMASA-2013-7.php
