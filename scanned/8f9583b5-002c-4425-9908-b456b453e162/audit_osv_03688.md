# [C] ALPINE-CVE-2026-42010

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-42010
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42010
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.13-r0

## Details
A flaw was found in gnutls. Servers configured with RSA-PSK (Rivest–Shamir–Adleman – Pre-Shared Key) wrongfully matched usernames containing a NUL character with truncated usernames. A remote attacker could exploit this by sending a specially crafted username, leading to an authentication bypass. This vulnerability allows an attacker to gain unauthorized access by circumventing the authentication process.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42010
