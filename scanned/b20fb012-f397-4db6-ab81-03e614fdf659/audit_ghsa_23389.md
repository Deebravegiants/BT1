# [M] phpMyAdmin XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vxj6-pm6r-23hq
CVE: CVE-2018-12581
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vxj6-pm6r-23hq
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.8.2

## Details
An issue was discovered in js/designer/move.js in phpMyAdmin before 4.8.2. A Cross-Site Scripting vulnerability has been found where an attacker can use a crafted database name to trigger an XSS attack when that database is referenced from the Designer feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12581
- https://github.com/phpmyadmin/phpmyadmin/commit/6943fff87324bd54c3a37a5160a5fb77498c355e
- https://web.archive.org/web/20210124181711/http://www.securityfocus.com/bid/104530
- https://web.archive.org/web/20210413204012/http://www.securitytracker.com/id/1041187
- https://www.phpmyadmin.net/security/PMASA-2018-3
