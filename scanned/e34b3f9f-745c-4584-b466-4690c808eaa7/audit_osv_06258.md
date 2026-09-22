# [H] Heap buffer overflow in array_merge()

## Summary
Severity: High
Advisory: BIT-libphp-2025-14178
Aliases: BIT-php-2025-14178, BIT-php-min-2025-14178, CVE-2025-14178, GHSA-h96m-rvf9-jgm2
Ecosystem: Bitnami
Published: 2026-01-08
Source: https://osv.dev/vulnerability/BIT-libphp-2025-14178
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.1

## Details
In PHP versions:8.1.* before 8.1.34, 8.2.* before 8.2.30, 8.3.* before 8.3.29, 8.4.* before 8.4.16, 8.5.* before 8.5.1, a heap buffer overflow occurs in array_merge() when the total element count of packed arrays exceeds 32-bit limits or HT_MAX_SIZE, due to an integer overflow in the precomputation of element counts using zend_hash_num_elements(). This may lead to memory corruption or crashes and affect the integrity and availability of the target server.

## References
- https://github.com/php/php-src/security/advisories/GHSA-h96m-rvf9-jgm2
- https://nvd.nist.gov/vuln/detail/CVE-2025-14178
- https://lists.debian.org/debian-lts-announce/2026/01/msg00019.html
