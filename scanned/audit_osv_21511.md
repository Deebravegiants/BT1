# [H] CVE-2021-43666

## Summary
Severity: High
Advisory: CVE-2021-43666
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-24
Source: https://osv.dev/vulnerability/CVE-2021-43666
Type: osv

## Details
A Denial of Service vulnerability exists in mbed TLS 3.0.0 and earlier in the mbedtls_pkcs12_derivation function when an input password's length is 0.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00034.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://github.com/ARMmbed/mbedtls/issues/5136
