# [C] ALPINE-CVE-2024-45158

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-45158
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45158
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.1-r0

## Details
An issue was discovered in Mbed TLS 3.6 before 3.6.1. A stack buffer overflow in mbedtls_ecdsa_der_to_raw() and mbedtls_ecdsa_raw_to_der() can occur when the bits parameter is larger than the largest supported curve. In some configurations with PSA disabled, all values of bits are affected. (This never happens in internal library calls, but can affect applications that call these functions directly.)

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45158
