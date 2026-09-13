# [C] ALPINE-CVE-2021-44732

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-44732
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44732
Type: osv

## Affected
- Alpine:v3.12: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.16.12-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.16.12-r0

## Details
Mbed TLS before 3.0.1 has a double free in certain out-of-memory conditions, as demonstrated by an mbedtls_ssl_set_session() failure.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44732
