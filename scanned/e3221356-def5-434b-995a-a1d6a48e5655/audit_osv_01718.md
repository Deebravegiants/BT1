# [H] ALPINE-CVE-2020-11501

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-11501
Ecosystem: Alpine:v3.10, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11501
Type: osv

## Affected
- Alpine:v3.10: `gnutls` — affected >=3.6.3 <3.6.8-r1
- Alpine:v3.12: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.13: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.14: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.15: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.16: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.17: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.18: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.19: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.20: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.21: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.22: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.23: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.24: `gnutls` — affected >=3.6.3 <3.6.13-r0
- Alpine:v3.8: `gnutls` — affected >=3.6.3 <3.6.7-r1
- Alpine:v3.9: `gnutls` — affected >=3.6.3 <3.6.7-r1

## Details
GnuTLS 3.6.x before 3.6.13 uses incorrect cryptography for DTLS. The earliest affected version is 3.6.3 (2018-07-16) because of an error in a 2017-10-06 commit. The DTLS client always uses 32 '\0' bytes instead of a random value, and thus contributes no randomness to a DTLS negotiation. This breaks the security guarantees of the DTLS protocol.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11501
