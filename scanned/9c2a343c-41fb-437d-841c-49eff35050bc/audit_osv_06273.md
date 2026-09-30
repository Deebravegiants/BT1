# [M] Null pointer dereference in php_mb_check_encoding() via mb_ereg_search_init()

## Summary
Severity: Medium
Advisory: BIT-libphp-2026-7259
Aliases: BIT-php-2026-7259, BIT-php-min-2026-7259, CVE-2026-7259
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-7259
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.2.* before 8.2.31, 8.3.* before 8.3.31, 8.4.* before 8.4.21, and 8.5.* before 8.5.6, a mismatch between encoding lists in Oniguruma and mbfl leads to  a NULL pointer dereference, resulting in a segmentation fault and denial of service. The vulnerability is exploitable when user-controlled input can influence the encoding passed to mb_regex_encoding().

## References
- https://github.com/php/php-src/security/advisories/GHSA-wm6j-2649-pv75
- https://nvd.nist.gov/vuln/detail/CVE-2026-7259
