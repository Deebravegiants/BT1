# [H] ALPINE-CVE-2026-12490

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-12490
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-12490
Type: osv

## Affected
- Alpine:v3.24: `nsd` — affected >=0 <4.14.3-r0

## Details
When a provide-xfr is given with a tls-auth-name, a secondary requesting a transfer should provide a client certificate with that name. However, no client certificate is needed when the request comes in over TLS over the regular tls-port (and not the tls-auth-port) or over over TCP over the regular port, when the other conditions of the provide-xfr rule match.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-12490
