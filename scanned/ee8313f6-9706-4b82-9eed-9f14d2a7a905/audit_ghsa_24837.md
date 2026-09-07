# [M] phpMyAdmin XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hmmx-wxh4-9w8w
CVE: CVE-2016-9857
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hmmx-wxh4-9w8w
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.9
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.18

## Details
An issue was discovered in phpMyAdmin. XSS is possible because of a weakness in a regular expression used in some JavaScript processing. All 4.6.x versions (prior to 4.6.5), 4.4.x versions (prior to 4.4.15.9), and 4.0.x versions (prior to 4.0.10.18) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9857
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20210123194716/http://www.securityfocus.com/bid/94530
- https://www.phpmyadmin.net/security/PMASA-2016-64
