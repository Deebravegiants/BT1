# [H] CVE-2018-9988

## Summary
Severity: High
Advisory: CVE-2018-9988
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-10
Source: https://osv.dev/vulnerability/CVE-2018-9988
Type: osv

## Details
ARM mbed TLS before 2.1.11, before 2.7.2, and before 2.8.0 has a buffer over-read in ssl_parse_server_key_exchange() that could cause a crash on invalid input.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00029.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00021.html
- https://tls.mbed.org/tech-updates/releases/mbedtls-2.8.0-2.7.2-and-2.1.11-released
- https://github.com/ARMmbed/mbedtls/commit/027f84c69f4ef30c0693832a6c396ef19e563ca1
- https://github.com/ARMmbed/mbedtls/commit/a1098f81c252b317ad34ea978aea2bc47760b215
