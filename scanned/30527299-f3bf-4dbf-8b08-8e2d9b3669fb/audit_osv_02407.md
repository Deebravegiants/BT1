# [M] ALPINE-CVE-2022-2097

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-2097
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2097
Type: osv

## Affected
- Alpine:v3.13: `openssl` — affected >=1.1.1 <1.1.1q-r0
- Alpine:v3.14: `openssl` — affected >=1.1.1 <1.1.1q-r0
- Alpine:v3.15: `openssl` — affected >=1.1.1 <1.1.1q-r0
- Alpine:v3.16: `openssl` — affected >=1.1.1 <1.1.1q-r0
- Alpine:v3.17: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.18: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.19: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <3.0.5-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.5-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.5-r0

## Details
AES OCB mode for 32-bit x86 platforms using the AES-NI assembly optimised implementation will not encrypt the entirety of the data under some circumstances. This could reveal sixteen bytes of data that was preexisting in the memory that wasn't written. In the special case of "in place" encryption, sixteen bytes of the plaintext would be revealed. Since OpenSSL does not support OCB based cipher suites for TLS and DTLS, they are both unaffected. Fixed in OpenSSL 3.0.5 (Affected 3.0.0-3.0.4). Fixed in OpenSSL 1.1.1q (Affected 1.1.1-1.1.1p).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2097
