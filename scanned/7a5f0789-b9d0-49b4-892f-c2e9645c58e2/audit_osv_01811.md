# [M] ALPINE-CVE-2020-16150

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-16150
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-16150
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.16.8-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.16.8-r0

## Details
A Lucky 13 timing side channel in mbedtls_ssl_decrypt_buf in library/ssl_msg.c in Trusted Firmware Mbed TLS through 2.23.0 allows an attacker to recover secret key information. This affects CBC mode because of a computed time difference based on a padding length.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-16150
