# [H] ALPINE-CVE-2025-48965

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-48965
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-48965
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.4-r0

## Details
Mbed TLS before 3.6.4 has a NULL pointer dereference because mbedtls_asn1_store_named_data can trigger conflicting data with val.p of NULL but val.len greater than zero.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-48965
