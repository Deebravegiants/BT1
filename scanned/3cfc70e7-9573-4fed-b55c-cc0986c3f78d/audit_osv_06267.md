# [C] SQL injection in ext-pgsql via E'...' backslash breakout

## Summary
Severity: Critical
Advisory: BIT-libphp-2026-17543
Aliases: BIT-php-2026-17543, BIT-php-min-2026-17543, CVE-2026-17543
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-libphp-2026-17543
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.9

## Details
Improper escaping of backslashes in attacker-provided parameters would allow for trivial SQL injection in PHP versions from 8.2.* before 8.2.33, from 8.3.* before 8.3.33, from 8.4.* before 8.4.24, and from 8.5.* before 8.5.9.

## References
- https://github.com/php/php-src/security/advisories/GHSA-7qpv-r5mr-78m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-17543
