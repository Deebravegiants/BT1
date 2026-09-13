# [M] ALPINE-CVE-2023-5981

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-5981
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5981
Type: osv

## Affected
- Alpine:v3.18: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.19: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.3-r0

## Details
A vulnerability was found that the response times to malformed ciphertexts in RSA-PSK ClientKeyExchange differ from response times of ciphertexts with correct PKCS#1 v1.5 padding.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5981
