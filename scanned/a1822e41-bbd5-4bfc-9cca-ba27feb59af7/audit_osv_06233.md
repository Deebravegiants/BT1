# [H] Array overrun in common path resolve code

## Summary
Severity: High
Advisory: BIT-libphp-2023-0568
Aliases: BIT-php-2023-0568, BIT-php-min-2023-0568, CVE-2023-0568
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2023-0568
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.2.0 <8.2.3

## Details
In PHP 8.0.X before 8.0.28, 8.1.X before 8.1.16 and 8.2.X before 8.2.3, core path resolution function allocate buffer one byte too small. When resolving paths with lengths close to system MAXPATHLEN setting, this may lead to the byte after the allocated buffer being overwritten with NUL value, which might lead to unauthorized data access or modification.

## References
- https://bugs.php.net/bug.php?id=81746
- https://nvd.nist.gov/vuln/detail/CVE-2023-0568
- https://security.netapp.com/advisory/ntap-20230517-0001/
