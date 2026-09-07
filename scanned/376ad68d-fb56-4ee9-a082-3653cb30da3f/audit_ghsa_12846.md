# [C] phpmyadmin contains SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-prcg-mc23-hgjh
CVE: CVE-2020-22452
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-prcg-mc23-hgjh
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=5.0.0 <5.0.2

## Details
SQL Injection vulnerability in function getTableCreationQuery in CreateAddField.php in phpMyAdmin 5.x before 5.0.2 via the tbl_storage_engine or tbl_collation parameters to tbl_create.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-22452
- https://github.com/phpmyadmin/phpmyadmin/issues/15898
- https://github.com/phpmyadmin/phpmyadmin/pull/16004
- https://github.com/phpmyadmin/phpmyadmin/commit/bc982466f08ddccad4804ba928f84ff8e25107cb
- https://github.com/phpmyadmin/phpmyadmin
