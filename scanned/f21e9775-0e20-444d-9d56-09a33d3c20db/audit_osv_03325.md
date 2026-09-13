# [M] ALPINE-CVE-2025-52497

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-52497
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-52497
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.4-r0

## Details
Mbed TLS before 3.6.4 has a PEM parsing one-byte heap-based buffer underflow, in mbedtls_pem_read_buffer and two mbedtls_pk_parse functions, via untrusted PEM input.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-52497
