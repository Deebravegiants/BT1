# [C] Out-of-bounds write in bccomp() via crafted operand and scale

## Summary
Severity: Critical
Advisory: BIT-libphp-2026-17544
Aliases: BIT-php-2026-17544, BIT-php-min-2026-17544, CVE-2026-17544
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-libphp-2026-17544
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.9

## Details
Attacker-provided inputs to bccomp() could lead to an out-of-bounds write with stack and heap corruption in PHP versions from 8.4.* before 8.4.24 and from 8.5.* before 8.5.9.

## References
- https://github.com/php/php-src/security/advisories/GHSA-x692-q9x7-8c3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-17544
