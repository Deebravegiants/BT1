# [M] CVE-2020-36425

## Summary
Severity: Medium
Advisory: CVE-2020-36425
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-07-19
Source: https://osv.dev/vulnerability/CVE-2020-36425
Type: osv

## Details
An issue was discovered in Arm Mbed TLS before 2.24.0. It incorrectly uses a revocationDate check when deciding whether to honor certificate revocation via a CRL. In some situations, an attacker can exploit this by changing the local clock.

## References
- https://github.com/ARMmbed/mbedtls/pull/3433
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.8
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.24.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.7.17
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://github.com/ARMmbed/mbedtls/issues/3340
- https://bugs.gentoo.org/740108
