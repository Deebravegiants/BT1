# [M] ALPINE-CVE-2024-28834

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-28834
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-28834
Type: osv

## Affected
- Alpine:v3.18: `gnutls` — affected >=0 <3.8.4-r0
- Alpine:v3.19: `gnutls` — affected >=0 <3.8.4-r0
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.5-r0

## Details
A flaw was found in GnuTLS. The Minerva attack is a cryptographic vulnerability that exploits deterministic behavior in systems like GnuTLS, leading to side-channel leaks. In specific scenarios, such as when using the GNUTLS_PRIVKEY_FLAG_REPRODUCIBLE flag, it can result in a noticeable step in nonce size from 513 to 512 bits, exposing a potential timing side-channel.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-28834
