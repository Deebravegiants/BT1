# [M] NULL Pointer Dereference in PHP SOAP Extension via Large XML Namespace Prefix

## Summary
Severity: Medium
Advisory: BIT-libphp-2025-6491
Aliases: BIT-php-2025-6491, BIT-php-min-2025-6491, CVE-2025-6491, GHSA-453j-q27h-5p8x
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-6491
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.10

## Details
In PHP versions:8.1.* before 8.1.33, 8.2.* before 8.2.29, 8.3.* before 8.3.23, 8.4.* before 8.4.10 when parsing XML data in SOAP extensions, overly large (>2Gb) XML namespace prefix may lead to null pointer dereference. This may lead to crashes and affect the availability of the target server.

## References
- https://github.com/php/php-src/security/advisories/GHSA-453j-q27h-5p8x
- https://nvd.nist.gov/vuln/detail/CVE-2025-6491
- http://www.openwall.com/lists/oss-security/2025/07/11/4
- https://lists.debian.org/debian-lts-announce/2025/07/msg00017.html
