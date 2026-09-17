# [H] Stream HTTP wrapper header check might omit basic auth header

## Summary
Severity: High
Advisory: BIT-libphp-2025-1736
Aliases: BIT-php-2025-1736, BIT-php-min-2025-1736, CVE-2025-1736, GHSA-hgf5-96fm-v528
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-1736
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.5

## Details
In PHP from 8.1.* before 8.1.32, from 8.2.* before 8.2.28, from 8.3.* before 8.3.19, from 8.4.* before 8.4.5, when user-supplied headers are sent, the insufficient validation of the end-of-line characters may prevent certain headers from being sent or lead to certain headers be misinterpreted.

## References
- https://github.com/php/php-src/security/advisories/GHSA-hgf5-96fm-v528
- https://nvd.nist.gov/vuln/detail/CVE-2025-1736
- https://security.netapp.com/advisory/ntap-20250523-0006/
- https://lists.debian.org/debian-lts-announce/2025/03/msg00014.html
