# [C] SQL injection in pdo_firebird via NUL bytes in quoted strings

## Summary
Severity: Critical
Advisory: BIT-libphp-2025-14179
Aliases: BIT-php-2025-14179, BIT-php-min-2025-14179, CVE-2025-14179
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2025-14179
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.2.* before 8.2.31, 8.3.* before 8.3.31, 8.4.* before 8.4.21, and 8.5.* before 8.5.6, the PDO Firebird driver improperly handles NUL bytes when preparing SQL queries. During token-by-token query construction, a string token containing a NUL byte is copied via strncat(), which stops at the NUL byte, dropping the closing quote and causing subsequent SQL tokens to be interpreted as part of the string. This allows SQL injection when attacker-controlled values are quoted via PDO::quote() and embedded in SQL statements.

## References
- https://github.com/php/php-src/security/advisories/GHSA-w476-322c-wpvm
- https://nvd.nist.gov/vuln/detail/CVE-2025-14179
- https://access.redhat.com/security/cve/CVE-2025-14179
- https://bugzilla.redhat.com/show_bug.cgi?id=2468567
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-14179.json
