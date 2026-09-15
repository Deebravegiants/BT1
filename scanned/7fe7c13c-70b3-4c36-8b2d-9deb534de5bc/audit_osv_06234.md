# [H] DoS vulnerability when parsing multipart request body

## Summary
Severity: High
Advisory: BIT-libphp-2023-0662
Aliases: BIT-php-2023-0662, BIT-php-min-2023-0662, CVE-2023-0662, GHSA-54hq-v5wp-fqgv
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2023-0662
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.2.0 <8.2.3

## Details
In PHP 8.0.X before 8.0.28, 8.1.X before 8.1.16 and 8.2.X before 8.2.3, excessive number of parts in HTTP form upload can cause high resource consumption and excessive number of log entries. This can cause denial of service on the affected server by exhausting CPU resources or disk space.

## References
- https://github.com/php/php-src/security/advisories/GHSA-54hq-v5wp-fqgv
- https://nvd.nist.gov/vuln/detail/CVE-2023-0662
- https://security.netapp.com/advisory/ntap-20230517-0001/
