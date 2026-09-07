# [M] phpMyAdmin Cross-site Scripting (XSS) in the import dialog

## Summary
Severity: Medium
Advisory: GHSA-c958-4j9x-q7w4
CVE: CVE-2018-15605
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c958-4j9x-q7w4
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.8.3

## Details
An issue was discovered in phpMyAdmin before 4.8.3. A Cross-Site Scripting vulnerability has been found where an attacker can use a crafted file to manipulate an authenticated user who loads that file through the import feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15605
- https://github.com/phpmyadmin/phpmyadmin/commit/00d90b3ae415b31338f76263359467a9fbebd0a1
- https://github.com/phpmyadmin/composer
- https://www.phpmyadmin.net/security/PMASA-2018-5
- http://www.securityfocus.com/bid/105168
- http://www.securitytracker.com/id/1041548
