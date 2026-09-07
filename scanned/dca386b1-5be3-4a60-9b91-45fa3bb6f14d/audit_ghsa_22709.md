# [M] phpMyAdmin Cross-site scripting (XSS) vulnerability in central columns feature

## Summary
Severity: Medium
Advisory: GHSA-gqmj-f46x-wqhw
CVE: CVE-2018-7260
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gqmj-f46x-wqhw
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.7.8

## Details
Cross-site scripting (XSS) vulnerability in db_central_columns.php in phpMyAdmin before 4.7.8 allows remote authenticated users to inject arbitrary web script or HTML via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7260
- https://github.com/phpmyadmin/phpmyadmin/commit/d2886a3
- https://github.com/phpmyadmin/composer
- https://udiniya.wordpress.com/2018/02/21/a-tale-of-stealing-session-cookie-in-phpmyadmin
- https://www.phpmyadmin.net/security/PMASA-2018-1
- http://www.securityfocus.com/bid/103099
