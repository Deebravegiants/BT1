# [H] ALPINE-CVE-2020-13777

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-13777
Ecosystem: Alpine:v3.10, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-13777
Type: osv

## Affected
- Alpine:v3.10: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.12: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.13: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.14: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.15: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.16: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.17: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.18: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.19: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.20: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.21: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.22: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.23: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.24: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.8: `gnutls` — affected >=3.6.0 <3.6.14-r0
- Alpine:v3.9: `gnutls` — affected >=3.6.0 <3.6.14-r0

## Details
GnuTLS 3.6.x before 3.6.14 uses incorrect cryptography for encrypting a session ticket (a loss of confidentiality in TLS 1.2, and an authentication bypass in TLS 1.3). The earliest affected version is 3.6.4 (2018-09-24) because of an error in a 2018-09-18 commit. Until the first key rotation, the TLS server always uses wrong data in place of an encryption key derived from an application.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-13777
