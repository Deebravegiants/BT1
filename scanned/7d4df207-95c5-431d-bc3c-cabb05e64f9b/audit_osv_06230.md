# [C] PDO::quote() may return unquoted string

## Summary
Severity: Critical
Advisory: BIT-libphp-2022-31631
Aliases: BIT-php-2022-31631, BIT-php-min-2022-31631, CVE-2022-31631
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2022-31631
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.2.0 <8.2.2

## Details
In PHP versions 8.0.* before 8.0.27, 8.1.* before 8.1.15, 8.2.* before 8.2.2 when using PDO::quote() function to quote user-supplied data for SQLite, supplying an overly long string may cause the driver to incorrectly quote the data, which may further lead to SQL injection vulnerabilities.

## References
- https://bugs.php.net/bug.php?id=81740
- https://nvd.nist.gov/vuln/detail/CVE-2022-31631
- https://security.netapp.com/advisory/ntap-20230223-0007/
