# [H] ALPINE-CVE-2024-23775

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-23775
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23775
Type: osv

## Affected
- Alpine:v3.16: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.28.7-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.28.7-r0

## Details
Integer Overflow vulnerability in Mbed TLS 2.x before 2.28.7 and 3.x before 3.5.2, allows attackers to cause a denial of service (DoS) via mbedtls_x509_set_extension().

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23775
