# [H] NULL Pointer Dereference in PDO quoting

## Summary
Severity: High
Advisory: BIT-libphp-2025-14180
Aliases: BIT-php-2025-14180, BIT-php-min-2025-14180, CVE-2025-14180, GHSA-8xr5-qppj-gvwj
Ecosystem: Bitnami
Published: 2026-01-08
Source: https://osv.dev/vulnerability/BIT-libphp-2025-14180
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.1

## Details
In PHP versions 8.1.* before 8.1.34, 8.2.* before 8.2.30, 8.3.* before 8.3.29, 8.4.* before 8.4.16, 8.5.* before 8.5.1 when using the PDO PostgreSQL driver with PDO::ATTR_EMULATE_PREPARES enabled, an invalid character sequence (such as \x99) in a prepared statement parameter may cause the quoting function PQescapeStringConn to return NULL, leading to a null pointer dereference in pdo_parse_params() function. This may lead to crashes (segmentation fault) and affect the availability of the target server.

## References
- https://github.com/php/php-src/security/advisories/GHSA-8xr5-qppj-gvwj
- https://nvd.nist.gov/vuln/detail/CVE-2025-14180
