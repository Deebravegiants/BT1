# [C] Stream HTTP wrapper truncates redirect location to 1024 bytes

## Summary
Severity: Critical
Advisory: BIT-libphp-2025-1861
Aliases: BIT-php-2025-1861, BIT-php-min-2025-1861, CVE-2025-1861, GHSA-52jp-hrpf-2jff
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-1861
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.5

## Details
In PHP from 8.1.* before 8.1.32, from 8.2.* before 8.2.28, from 8.3.* before 8.3.19, from 8.4.* before 8.4.5, when parsing HTTP redirect in the response to an HTTP request, there is currently limit on the location value size caused by limited size of the location buffer to 1024. However as per RFC9110, the limit is recommended to be 8000. This may lead to incorrect URL truncation and redirecting to a wrong location.

## References
- https://github.com/php/php-src/security/advisories/GHSA-52jp-hrpf-2jff
- https://nvd.nist.gov/vuln/detail/CVE-2025-1861
- https://security.netapp.com/advisory/ntap-20250523-0005/
- https://lists.debian.org/debian-lts-announce/2025/03/msg00014.html
