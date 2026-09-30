# [H] CVE-2020-36476

## Summary
Severity: High
Advisory: CVE-2020-36476
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2020-36476
Type: osv

## Details
An issue was discovered in Mbed TLS before 2.24.0 (and before 2.16.8 LTS and before 2.7.17 LTS). There is missing zeroization of plaintext buffers in mbedtls_ssl_read to erase unused application data from memory.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.16.8
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.24.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.7.17
- https://lists.debian.org/debian-lts-announce/2021/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
