# [M] phpMyAdmin Multiple cross-site scripting (XSS) vulnerabilities 

## Summary
Severity: Medium
Advisory: GHSA-5gh4-v2ch-pcx4
CVE: CVE-2013-4997
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5gh4-v2ch-pcx4
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.5 <3.5.8.2

## Details
Multiple cross-site scripting (XSS) vulnerabilities in phpMyAdmin 3.5.x before 3.5.8.2 allow remote attackers to inject arbitrary web script or HTML via vectors involving a JavaScript event in (1) an anchor identifier to setup/index.php or (2) a chartTitle (aka chart title) value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4997
- https://github.com/phpmyadmin/composer
- http://www.phpmyadmin.net/home_page/security/PMASA-2013-9.php
