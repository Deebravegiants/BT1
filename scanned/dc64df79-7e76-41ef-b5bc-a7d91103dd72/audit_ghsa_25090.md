# [H] phpMyAdmin CSRF vulnerability allowing arbitrary SQL execution

## Summary
Severity: High
Advisory: GHSA-v6fp-h79x-9rqc
CVE: CVE-2018-10188
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v6fp-h79x-9rqc
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.8 <4.8.0.1

## Details
phpMyAdmin 4.8.0 before 4.8.0-1 has CSRF, allowing an attacker to execute arbitrary SQL statements, related to js/db_operations.js, js/tbl_operations.js, libraries/classes/Operations.php, and sql.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10188
- https://github.com/phpmyadmin/phpmyadmin/commit/c6dd6b56e236a3aff953cee4135ecaa67130e641
- https://github.com/phpmyadmin/composer
- https://www.exploit-db.com/exploits/44496
- https://www.phpmyadmin.net/security/PMASA-2018-2
- http://www.securityfocus.com/bid/103936
- http://www.securitytracker.com/id/1040752
