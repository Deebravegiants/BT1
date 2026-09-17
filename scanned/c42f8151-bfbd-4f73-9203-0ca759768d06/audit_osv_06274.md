# [M] Stack overflow in phar with circular symlinks

## Summary
Severity: Medium
Advisory: BIT-libphp-2026-7260
Aliases: BIT-php-2026-7260, BIT-php-min-2026-7260, CVE-2026-7260
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-libphp-2026-7260
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.9

## Details
Circular symbolic links in phar archives could lead to unbounded recursion, exhausting the C stack and crashing the PHP process, in PHP versions from 8.2.* before 8.2.33, from 8.3.* before 8.3.33, from 8.4.* before 8.4.24, and from 8.5.* before 8.5.9.

## References
- https://github.com/php/php-src/security/advisories/GHSA-vc5h-9ppw-p5f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-7260
