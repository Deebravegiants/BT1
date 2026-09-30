# [M] ALPINE-CVE-2025-54764

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-54764
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-54764
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.5-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.5-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.5-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.5-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.5-r0

## Details
Mbed TLS before 3.6.5 allows a local timing attack against certain RSA operations, and direct calls to mbedtls_mpi_mod_inv or mbedtls_mpi_gcd.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-54764
