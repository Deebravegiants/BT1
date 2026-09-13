# [C] ALPINE-CVE-2022-35409

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-35409
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-35409
Type: osv

## Affected
- Alpine:v3.16: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.28.1-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.28.1-r0

## Details
An issue was discovered in Mbed TLS before 2.28.1 and 3.x before 3.2.0. In some configurations, an unauthenticated attacker can send an invalid ClientHello message to a DTLS server that causes a heap-based buffer over-read of up to 255 bytes. This can cause a server crash or possibly information disclosure based on error responses. Affected configurations have MBEDTLS_SSL_DTLS_CLIENT_PORT_REUSE enabled and MBEDTLS_SSL_IN_CONTENT_LEN less than a threshold that depends on the configuration: 258 bytes if using mbedtls_ssl_cookie_check, and possibly up to 571 bytes with a custom cookie check function.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-35409
