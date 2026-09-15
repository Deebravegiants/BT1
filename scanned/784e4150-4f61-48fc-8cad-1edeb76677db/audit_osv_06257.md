# [H] Information Leak of Memory in getimagesize

## Summary
Severity: High
Advisory: BIT-libphp-2025-14177
Aliases: BIT-php-2025-14177, BIT-php-min-2025-14177, CVE-2025-14177, GHSA-3237-qqm7-mfv7
Ecosystem: Bitnami
Published: 2026-01-08
Source: https://osv.dev/vulnerability/BIT-libphp-2025-14177
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.1

## Details
In PHP versions:8.1.* before 8.1.34, 8.2.* before 8.2.30, 8.3.* before 8.3.29, 8.4.* before 8.4.16, 8.5.* before 8.5.1, the getimagesize() function may leak uninitialized heap memory into the APPn segments (e.g., APP1) when reading images in multi-chunk mode (such as via php://filter). This occurs due to a bug in php_read_stream_all_chunks() that overwrites the buffer without advancing the pointer, leaving tail bytes uninitialized. This may lead to information disclosure of sensitive heap data and affect the confidentiality of the target server.

## References
- https://github.com/php/php-src/security/advisories/GHSA-3237-qqm7-mfv7
- https://nvd.nist.gov/vuln/detail/CVE-2025-14177
