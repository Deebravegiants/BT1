# [M] ALPINE-CVE-2024-45157

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-45157
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45157
Type: osv

## Affected
- Alpine:v3.17: `mbedtls` — affected >=0 <2.28.9-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.28.9-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.28.9-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.1-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.1-r0

## Details
An issue was discovered in Mbed TLS before 2.28.9 and 3.x before 3.6.1, in which the user-selected algorithm is not used. Unlike previously documented, enabling MBEDTLS_PSA_HMAC_DRBG_MD_TYPE does not cause the PSA subsystem to use HMAC_DRBG: it uses HMAC_DRBG only when MBEDTLS_PSA_CRYPTO_EXTERNAL_RNG and MBEDTLS_CTR_DRBG_C are disabled.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45157
