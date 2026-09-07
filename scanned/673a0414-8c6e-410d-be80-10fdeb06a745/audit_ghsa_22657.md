# [H] phpMyAdmin Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-gg36-9346-9qx9
CVE: CVE-2013-3239
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gg36-9346-9qx9
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.5.0 <3.5.8.1

## Details
phpMyAdmin 3.5.x before 3.5.8 and 4.x before 4.0.0-rc3, when a SaveDir directory is configured, allows remote authenticated users to execute arbitrary code by using a double extension in the filename of an export file, leading to interpretation of this file as an executable file by the Apache HTTP Server, as demonstrated by a .php.sql filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-3239
- https://github.com/phpmyadmin/phpmyadmin/commit/1f6bc0b707002e26cab216b9e57b4d5de764de48
- https://github.com/phpmyadmin/phpmyadmin/commit/d3fafdfba0807068196655e9b6d16c5d1d3ccf8a
- https://github.com/phpmyadmin/phpmyadmin
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/104725.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/104770.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/104936.html
- http://lists.opensuse.org/opensuse-updates/2013-06/msg00181.html
- http://www.phpmyadmin.net/home_page/security/PMASA-2013-3.php
