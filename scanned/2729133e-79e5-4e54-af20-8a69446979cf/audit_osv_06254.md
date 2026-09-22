# [M] Header parser of http stream wrapper does not handle folded headers

## Summary
Severity: Medium
Advisory: BIT-libphp-2025-1217
Aliases: BIT-php-2025-1217, BIT-php-min-2025-1217, CVE-2025-1217, GHSA-v8xr-gpvj-cx9g
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-1217
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.5

## Details
In PHP from 8.1.* before 8.1.32, from 8.2.* before 8.2.28, from 8.3.* before 8.3.19, from 8.4.* before 8.4.5, when http request module parses HTTP response obtained from a server, folded headers are parsed incorrectly, which may lead to misinterpreting the response and using incorrect headers, MIME types, etc.

## References
- https://github.com/php/php-src/security/advisories/GHSA-v8xr-gpvj-cx9g
- https://nvd.nist.gov/vuln/detail/CVE-2025-1217
- https://security.netapp.com/advisory/ntap-20250523-0008/
- https://lists.debian.org/debian-lts-announce/2025/03/msg00014.html
