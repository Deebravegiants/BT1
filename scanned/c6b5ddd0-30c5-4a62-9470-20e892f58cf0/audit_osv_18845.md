# [H] CVE-2020-36475

## Summary
Severity: High
Advisory: CVE-2020-36475
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2020-36475
Type: osv

## Details
An issue was discovered in Mbed TLS before 2.25.0 (and before 2.16.9 LTS and before 2.7.18 LTS). The calculations performed by mbedtls_mpi_exp_mod are not limited; thus, supplying overly large parameters could lead to denial of service when generating Diffie-Hellman key pairs.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.9
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.25.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.7.18
- https://lists.debian.org/debian-lts-announce/2021/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-756638.pdf
