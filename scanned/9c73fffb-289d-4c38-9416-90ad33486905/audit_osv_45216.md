# [H] A Denial of Service vulnerability exists in mbed TLS 3.0.0 and earlier in the...

## Summary
Severity: High
Advisory: JLSEC-2025-217
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-217
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.0+0

## Details
A Denial of Service vulnerability exists in mbed TLS 3.0.0 and earlier in the `mbedtls_pkcs12_derivation` function when an input password's length is 0.

## References
- https://github.com/ARMmbed/mbedtls/issues/5136
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.debian.org/debian-lts-announce/2025/06/msg00034.html
