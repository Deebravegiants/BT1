# [M] ALPINE-CVE-2025-27809

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-27809
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27809
Type: osv

## Affected
- Alpine:v3.18: `mbedtls` — affected >=0 <2.28.10-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.28.10-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.3-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.3-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.3-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.3-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.3-r0

## Details
Mbed TLS before 2.28.10 and 3.x before 3.6.3, on the client side, accepts servers that have trusted certificates for arbitrary hostnames unless the TLS client application calls mbedtls_ssl_set_hostname.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27809
