# [M] ALPINE-CVE-2018-19608

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-19608
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19608
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.14.1-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.14.1-r0

## Details
Arm Mbed TLS before 2.14.1, before 2.7.8, and before 2.1.17 allows a local unprivileged attacker to recover the plaintext of RSA decryption, which is used in RSA-without-(EC)DH(E) cipher suites.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19608
