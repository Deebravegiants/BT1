# [H] ALPINE-CVE-2017-7507

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7507
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7507
Type: osv

## Affected
- Alpine:v3.10: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.11: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.12: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.13: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.14: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.15: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.16: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.17: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.18: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.19: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.20: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.3: `gnutls` — affected >=0 <3.14.17-r1
- Alpine:v3.4: `gnutls` — affected >=0 <3.14.17-r1
- Alpine:v3.5: `gnutls` — affected >=0 <3.14.17-r1
- Alpine:v3.6: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.7: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.8: `gnutls` — affected >=0 <3.5.13-r0
- Alpine:v3.9: `gnutls` — affected >=0 <3.5.13-r0

## Details
GnuTLS version 3.5.12 and earlier is vulnerable to a NULL pointer dereference while decoding a status response TLS extension with valid contents. This could lead to a crash of the GnuTLS server application.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7507
