# [H] CVE-2020-36478

## Summary
Severity: High
Advisory: CVE-2020-36478
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2020-36478
Type: osv

## Details
An issue was discovered in Mbed TLS before 2.25.0 (and before 2.16.9 LTS and before 2.7.18 LTS). A NULL algorithm parameters entry looks identical to an array of REAL (size zero) and thus the certificate is considered valid. However, if the parameters do not match in any way, then the certificate should be considered invalid.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.9
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.25.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.7.18
- https://lists.debian.org/debian-lts-announce/2021/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-756638.pdf
- https://github.com/ARMmbed/mbedtls/issues/3629
