# [M] Leak partial content of the heap through heap buffer over-read in mysqlnd

## Summary
Severity: Medium
Advisory: BIT-libphp-2024-8929
Aliases: BIT-php-2024-8929, BIT-php-min-2024-8929, CVE-2024-8929, GHSA-h35g-vwh6-m678
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-8929
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.14

## Details
In PHP versions 8.1.* before 8.1.31, 8.2.* before 8.2.26, 8.3.* before 8.3.14, a hostile MySQL server can cause the client to disclose the content of its heap containing data from other SQL requests and possible other data belonging to different users of the same server.

## References
- https://github.com/php/php-src/security/advisories/GHSA-h35g-vwh6-m678
- https://nvd.nist.gov/vuln/detail/CVE-2024-8929
- https://security.netapp.com/advisory/ntap-20250110-0008/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00007.html
