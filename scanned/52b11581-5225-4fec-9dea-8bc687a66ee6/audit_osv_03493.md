# [H] ALPINE-CVE-2026-21637

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-21637
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21637
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.14.1-r0

## Details
A flaw in Node.js TLS error handling allows remote attackers to crash or exhaust resources of a TLS server when `pskCallback` or `ALPNCallback` are in use. Synchronous exceptions thrown during these callbacks bypass standard TLS error handling paths (tlsClientError and error), causing either immediate process termination or silent file descriptor leaks that eventually lead to denial of service. Because these callbacks process attacker-controlled input during the TLS handshake, a remote client can repeatedly trigger the issue. This vulnerability affects TLS servers using PSK or ALPN callbacks across Node.js versions where these callbacks throw without being safely wrapped.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21637
