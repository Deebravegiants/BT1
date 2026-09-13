# [H] ALPINE-CVE-2025-52496

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-52496
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-52496
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.4-r0

## Details
Mbed TLS before 3.6.4 has a race condition in AESNI detection if certain compiler optimizations occur. An attacker may be able to extract an AES key from a multithreaded program, or perform a GCM forgery.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-52496
