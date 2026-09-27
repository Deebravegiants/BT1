# [M] ALPINE-CVE-2019-18222

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-18222
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-01-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18222
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.16.4-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.16.4-r0

## Details
The ECDSA signature implementation in ecdsa.c in Arm Mbed Crypto 2.1 and Mbed TLS through 2.19.1 does not reduce the blinded scalar before computing the inverse, which allows a local attacker to recover the private key via side-channel attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18222
