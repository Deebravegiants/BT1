# [M] ALPINE-CVE-2024-23170

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-23170
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23170
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
An issue was discovered in Mbed TLS 2.x before 2.28.7 and 3.x before 3.5.2. There was a timing side channel in RSA private operations. This side channel could be sufficient for a local attacker to recover the plaintext. It requires the attacker to send a large number of messages for decryption, as described in "Everlasting ROBOT: the Marvin Attack" by Hubert Kario.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23170
