# [M] Mbed TLS before 3.6.4 has a PEM parsing one-byte heap-based buffer underflow, in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-229
Ecosystem: Julia
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-229
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.1010+0

## Details
Mbed TLS before 3.6.4 has a PEM parsing one-byte heap-based buffer underflow, in `mbedtls_pem_read_buffer` and two `mbedtls_pk_parse` functions, via untrusted PEM input.

## References
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-2.md
- https://lists.debian.org/debian-lts-announce/2025/08/msg00013.html
