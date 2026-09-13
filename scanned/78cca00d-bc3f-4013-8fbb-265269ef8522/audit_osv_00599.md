# [C] ALPINE-CVE-2017-18187

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-18187
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-18187
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.7.0-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.7.0-r0

## Details
In ARM mbed TLS before 2.7.0, there is a bounds-check bypass through an integer overflow in PSK identity parsing in the ssl_parse_client_psk_identity() function in library/ssl_srv.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-18187
