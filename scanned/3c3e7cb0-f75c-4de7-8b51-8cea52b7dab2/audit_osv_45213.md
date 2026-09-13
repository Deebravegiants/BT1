# [C] Mbed TLS before 3.0.1 has a double free in certain out-of-memory conditions, as demonstrated by an...

## Summary
Severity: Critical
Advisory: JLSEC-2025-214
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-214
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.0+0

## Details
Mbed TLS before 3.0.1 has a double free in certain out-of-memory conditions, as demonstrated by an `mbedtls_ssl_set_session()` failure.

## References
- https://bugs.gentoo.org/829660
- https://github.com/ARMmbed/mbedtls/releases
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.12
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.28.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v3.1.0
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.debian.org/debian-lts-announce/2025/06/msg00034.html
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2021-12
