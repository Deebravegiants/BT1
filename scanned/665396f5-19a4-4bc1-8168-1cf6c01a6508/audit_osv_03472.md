# [H] ALPINE-CVE-2026-1584

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-1584
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-1584
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.12-r0

## Details
A flaw was found in gnutls. A remote, unauthenticated attacker can exploit this vulnerability by sending a specially crafted ClientHello message with an invalid Pre-Shared Key (PSK) binder value during the TLS handshake. This can lead to a NULL pointer dereference, causing the server to crash and resulting in a remote Denial of Service (DoS) condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-1584
