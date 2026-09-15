# [C] ALPINE-CVE-2024-45159

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-45159
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45159
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.1-r0

## Details
An issue was discovered in Mbed TLS 3.x before 3.6.1. With TLS 1.3, when a server enables optional authentication of the client, if the client-provided certificate does not have appropriate values in if keyUsage or extKeyUsage extensions, then the return value of mbedtls_ssl_get_verify_result() would incorrectly have the MBEDTLS_X509_BADCERT_KEY_USAGE and MBEDTLS_X509_BADCERT_KEY_USAGE bits clear. As a result, an attacker that had a certificate valid for uses other than TLS client authentication would nonetheless be able to use it for TLS client authentication. Only TLS 1.3 servers were affected, and only with optional authentication (with required authentication, the handshake would be aborted with a fatal alert).

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45159
