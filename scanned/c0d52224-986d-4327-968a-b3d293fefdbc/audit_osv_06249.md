# [M] Erroneous parsing of multipart form data

## Summary
Severity: Medium
Advisory: BIT-libphp-2024-8925
Aliases: BIT-php-2024-8925, BIT-php-min-2024-8925, CVE-2024-8925, GHSA-9pqp-7h25-4f32
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-8925
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.12

## Details
In PHP versions 8.1.* before 8.1.30, 8.2.* before 8.2.24, 8.3.* before 8.3.12, erroneous parsing of multipart form data contained in an HTTP POST request could lead to legitimate data not being processed. This could lead to malicious attacker able to control part of the submitted data being able to exclude portion of other data, potentially leading to erroneous application behavior.

## References
- https://github.com/php/php-src/security/advisories/GHSA-9pqp-7h25-4f32
- https://nvd.nist.gov/vuln/detail/CVE-2024-8925
- https://lists.debian.org/debian-lts-announce/2024/10/msg00011.html
- https://security.netapp.com/advisory/ntap-20241101-0003/
