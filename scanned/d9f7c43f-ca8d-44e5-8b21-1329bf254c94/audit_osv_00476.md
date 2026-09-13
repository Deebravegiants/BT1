# [H] ALPINE-CVE-2017-14032

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14032
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14032
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.6.0-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.6.0-r0

## Details
ARM mbed TLS before 1.3.21 and 2.x before 2.1.9, if optional authentication is configured, allows remote attackers to bypass peer authentication via an X.509 certificate chain with many intermediates. NOTE: although mbed TLS was formerly known as PolarSSL, the releases shipped with the PolarSSL name are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14032
