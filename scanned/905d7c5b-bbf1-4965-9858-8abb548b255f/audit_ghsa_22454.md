# [M] phpMyAdmin Cross-site scripting (XSS) vulnerability in SQL parser

## Summary
Severity: Medium
Advisory: GHSA-7rf8-9r8f-qf59
CVE: CVE-2016-2559
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7rf8-9r8f-qf59
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.5 <4.5.5.1

## Details
Cross-site scripting (XSS) vulnerability in the format function in libraries/sql-parser/src/Utils/Error.php in the SQL parser in phpMyAdmin 4.5.x before 4.5.5.1 allows remote authenticated users to inject arbitrary web script or HTML via a crafted query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2559
- https://github.com/phpmyadmin/phpmyadmin/commit/3a6a9a807d99371ee126635e1a505fc1fe0df32c
- https://github.com/phpmyadmin/composer
- https://www.phpmyadmin.net/security/PMASA-2016-10
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178562.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178869.html
