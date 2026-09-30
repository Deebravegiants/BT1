# [H] ALPINE-CVE-2017-2784

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-2784
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2784
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.4.2-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.4.2-r0

## Details
An exploitable free of a stack pointer vulnerability exists in the x509 certificate parsing code of ARM mbed TLS before 1.3.19, 2.x before 2.1.7, and 2.4.x before 2.4.2. A specially crafted x509 certificate, when parsed by mbed TLS library, can cause an invalid free of a stack pointer leading to a potential remote code execution. In order to exploit this vulnerability, an attacker can act as either a client or a server on a network to deliver malicious x509 certificates to vulnerable applications.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2784
