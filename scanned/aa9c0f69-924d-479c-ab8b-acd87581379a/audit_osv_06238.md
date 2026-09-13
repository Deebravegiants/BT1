# [H] Single byte overread with convert.quoted-printable-decode filter

## Summary
Severity: High
Advisory: BIT-libphp-2024-11233
Aliases: BIT-php-2024-11233, BIT-php-min-2024-11233, CVE-2024-11233, GHSA-r977-prxv-hc43
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-11233
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.14

## Details
In PHP versions 8.1.* before 8.1.31, 8.2.* before 8.2.26, 8.3.* before 8.3.14, due to an error in convert.quoted-printable-decode filter certain data can lead to buffer overread by one byte, which can in certain circumstances lead to crashes or disclose content of other memory areas.

## References
- https://github.com/php/php-src/security/advisories/GHSA-r977-prxv-hc43
- https://nvd.nist.gov/vuln/detail/CVE-2024-11233
- https://lists.debian.org/debian-lts-announce/2024/12/msg00007.html
- https://security.netapp.com/advisory/ntap-20241220-0008/
