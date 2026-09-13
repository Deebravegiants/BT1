# [C] CVE-2021-44732

## Summary
Severity: Critical
Advisory: CVE-2021-44732
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-20
Source: https://osv.dev/vulnerability/CVE-2021-44732
Type: osv

## Details
Mbed TLS before 3.0.1 has a double free in certain out-of-memory conditions, as demonstrated by an mbedtls_ssl_set_session() failure.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00034.html
- https://github.com/ARMmbed/mbedtls/releases
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.12
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.28.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v3.1.0
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://bugs.gentoo.org/829660
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2021-12
