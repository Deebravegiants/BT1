# [H] ALPINE-CVE-2019-3829

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-3829
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3829
Type: osv

## Affected
- Alpine:v3.10: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.11: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.12: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.13: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.14: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.15: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.16: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.17: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.18: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.19: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.20: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.21: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.22: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.23: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.24: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.8: `gnutls` — affected >=3.5.8 <3.6.7-r0
- Alpine:v3.9: `gnutls` — affected >=3.5.8 <3.6.7-r0

## Details
A vulnerability was found in gnutls versions from 3.5.8 before 3.6.7. A memory corruption (double free) vulnerability in the certificate verification API. Any client or server application that verifies X.509 certificates with GnuTLS 3.5.8 or later is affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3829
