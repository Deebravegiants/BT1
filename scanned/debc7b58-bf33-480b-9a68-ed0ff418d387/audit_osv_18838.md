# [M] CVE-2020-36421

## Summary
Severity: Medium
Advisory: CVE-2020-36421
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-07-19
Source: https://osv.dev/vulnerability/CVE-2020-36421
Type: osv

## Details
An issue was discovered in Arm Mbed TLS before 2.23.0. Because of a side channel in modular exponentiation, an RSA private key used in a secure enclave could be disclosed.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.7
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.23.0
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://github.com/ARMmbed/mbedtls/issues/3394
- https://bugs.gentoo.org/730752
