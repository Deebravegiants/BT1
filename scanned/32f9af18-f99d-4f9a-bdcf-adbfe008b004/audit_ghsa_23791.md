# [M] phpMyAdmin XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gcvp-cwgw-wx8j
CVE: CVE-2016-5704
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gcvp-cwgw-wx8j
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.3

## Details
Cross-site scripting (XSS) vulnerability in the table-structure page in phpMyAdmin 4.6.x before 4.6.3 allows remote attackers to inject arbitrary web script or HTML via vectors involving a comment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5704
- https://github.com/phpmyadmin/phpmyadmin/commit/72213573182896bd6a6e5af5ba1881dd87c4a20b
- https://github.com/phpmyadmin/phpmyadmin
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-20
