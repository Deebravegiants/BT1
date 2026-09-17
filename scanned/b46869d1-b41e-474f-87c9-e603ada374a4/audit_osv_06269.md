# [C] Global buffer over-read in mb_convert_encoding() with attacker-supplied encoding

## Summary
Severity: Critical
Advisory: BIT-libphp-2026-6104
Aliases: BIT-php-2026-6104, BIT-php-min-2026-6104, CVE-2026-6104
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-6104
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.4.* before 8.4.21 and 8.5.* before 8.5.6, when an encoding name containing an embedded NUL byte is passed to mb_convert_encoding() or related mbstring functions, the code incorrectly assumes that when strncasecmp() returns 0 it means the strings have the same length. This can lead to out-of-bounds read of global memory, potentially causing a crash or information disclosure or crash. Affected functions include mb_convert_encoding(), mb_detect_encoding(), mb_convert_variables(), and mb_detect_order(), as well as the mbstring.detect_order and mbstring.http_output INI settings.

## References
- https://github.com/php/php-src/security/advisories/GHSA-74r9-qxhc-fx53
- https://nvd.nist.gov/vuln/detail/CVE-2026-6104
- https://access.redhat.com/errata/RHSA-2026:22649
- https://access.redhat.com/security/cve/CVE-2026-6104
- https://bugzilla.redhat.com/show_bug.cgi?id=2468573
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-6104.json
