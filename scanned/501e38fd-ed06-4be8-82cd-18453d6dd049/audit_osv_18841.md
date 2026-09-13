# [M] CVE-2020-36424

## Summary
Severity: Medium
Advisory: CVE-2020-36424
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-19
Source: https://osv.dev/vulnerability/CVE-2020-36424
Type: osv

## Details
An issue was discovered in Arm Mbed TLS before 2.24.0. An attacker can recover a private key (for RSA or static Diffie-Hellman) via a side-channel attack against generation of base blinding/unblinding values.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.8
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.24.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.7.17
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2020-09-2
- https://bugs.gentoo.org/740108
