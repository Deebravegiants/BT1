# [H] ALPINE-CVE-2026-80229

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-80229
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-80229
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
When performing transfers via libcurl’s multi interface, pooled TLS
connections can outlive their originating easy handles. In OpenSSL 3 provider
configurations, libcurl attaches an allocated library context to the easy
handle's state and passes it to OpenSSL without acquiring an ownership
reference; destroying the easy handle prematurely frees this context while the
active connection retains a dangling pointer, leading to a heap-use-after-free
upon subsequent I/O or post-handshake operations.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-80229
