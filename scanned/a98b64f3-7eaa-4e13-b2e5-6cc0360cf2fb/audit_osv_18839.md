# [M] CVE-2020-36422

## Summary
Severity: Medium
Advisory: CVE-2020-36422
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-07-19
Source: https://osv.dev/vulnerability/CVE-2020-36422
Type: osv

## Details
An issue was discovered in Arm Mbed TLS before 2.23.0. A side channel allows recovery of an ECC private key, related to mbedtls_ecp_check_pub_priv, mbedtls_pk_parse_key, mbedtls_pk_parse_keyfile, mbedtls_ecp_mul, and mbedtls_ecp_mul_restartable.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.7
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.23.0
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://bugs.gentoo.org/730752
