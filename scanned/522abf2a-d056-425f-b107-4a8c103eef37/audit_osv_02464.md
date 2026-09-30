# [H] ALPINE-CVE-2022-2509

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-2509
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2509
Type: osv

## Affected
- Alpine:v3.13: `gnutls` — affected >=0 <3.7.1-r1
- Alpine:v3.14: `gnutls` — affected >=0 <3.7.1-r1
- Alpine:v3.15: `gnutls` — affected >=0 <3.7.1-r1
- Alpine:v3.16: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.17: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.18: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.19: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.20: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.7.7-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.7.7-r0

## Details
A vulnerability found in gnutls. This security flaw happens because of a double free error occurs during verification of pkcs7 signatures in gnutls_pkcs7_verify function.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2509
