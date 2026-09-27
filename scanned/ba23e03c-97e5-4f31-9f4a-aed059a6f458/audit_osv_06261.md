# [M] Streams HTTP wrapper does not fail for headers with invalid name and no colon

## Summary
Severity: Medium
Advisory: BIT-libphp-2025-1734
Aliases: BIT-php-2025-1734, BIT-php-min-2025-1734, CVE-2025-1734, GHSA-pcmh-g36c-qc44
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-1734
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.5

## Details
In PHP from 8.1.* before 8.1.32, from 8.2.* before 8.2.28, from 8.3.* before 8.3.19, from 8.4.* before 8.4.5, when receiving headers from HTTP server, the headers missing a colon (:) are treated as valid headers even though they are not. This may confuse applications into accepting invalid headers.

## References
- https://github.com/php/php-src/security/advisories/GHSA-pcmh-g36c-qc44
- https://nvd.nist.gov/vuln/detail/CVE-2025-1734
- https://security.netapp.com/advisory/ntap-20250523-0009/
- https://lists.debian.org/debian-lts-announce/2025/03/msg00014.html
