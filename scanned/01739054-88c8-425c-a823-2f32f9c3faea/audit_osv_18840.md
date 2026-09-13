# [H] CVE-2020-36423

## Summary
Severity: High
Advisory: CVE-2020-36423
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-19
Source: https://osv.dev/vulnerability/CVE-2020-36423
Type: osv

## Details
An issue was discovered in Arm Mbed TLS before 2.23.0. A remote attacker can recover plaintext because a certain Lucky 13 countermeasure doesn't properly consider the case of a hardware accelerator.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.7
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.23.0
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://bugs.gentoo.org/730752
