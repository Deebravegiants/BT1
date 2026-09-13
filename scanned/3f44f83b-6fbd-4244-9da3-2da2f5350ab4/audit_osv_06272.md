# [H] Out-of-bounds read in urldecode() on NetBSD

## Summary
Severity: High
Advisory: BIT-libphp-2026-7258
Aliases: BIT-php-2026-7258, BIT-php-min-2026-7258, CVE-2026-7258, GHSA-m8rr-4c36-8gq4
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-7258
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.2.* before 8.2.31, 8.3.* before 8.3.31, 8.4.* before 8.4.21, and 8.5.* before 8.5.6, some functions, including urldecode(), pass signed char to ctype functions (like isxdigit()). On the systems with default signed char and optimized table-lookup ctype functions - such as NetBSD - this can lead to accessing array with negative offset, which can trigger a denial of service.

## References
- https://github.com/php/php-src/security/advisories/GHSA-m8rr-4c36-8gq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-7258
