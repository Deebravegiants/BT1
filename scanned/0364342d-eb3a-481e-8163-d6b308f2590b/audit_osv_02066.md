# [C] ALPINE-CVE-2021-20232

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-20232
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20232
Type: osv

## Affected
- Alpine:v3.10: `gnutls` — affected >=3.6.3 <3.6.15-r1
- Alpine:v3.11: `gnutls` — affected >=3.6.3 <3.6.15-r1
- Alpine:v3.12: `gnutls` — affected >=3.6.3 <3.6.15-r1
- Alpine:v3.13: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.14: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.15: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.16: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.17: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.18: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.19: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.20: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.21: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.22: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.23: `gnutls` — affected >=3.6.3 <3.7.1-r0
- Alpine:v3.24: `gnutls` — affected >=3.6.3 <3.7.1-r0

## Details
A flaw was found in gnutls. A use after free issue in client_send_params in lib/ext/pre_shared_key.c may lead to memory corruption and other potential consequences.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20232
