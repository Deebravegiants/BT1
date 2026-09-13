# [M] ALPINE-CVE-2019-16910

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-16910
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-16910
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.16.3-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.16.3-r0

## Details
Arm Mbed TLS before 2.19.0 and Arm Mbed Crypto before 2.0.0, when deterministic ECDSA is enabled, use an RNG with insufficient entropy for blinding, which might allow an attacker to recover a private key via side-channel attacks if a victim signs the same message many times. (For Mbed TLS, the fix is also available in versions 2.7.12 and 2.16.3.)

## References
- https://security.alpinelinux.org/vuln/CVE-2019-16910
