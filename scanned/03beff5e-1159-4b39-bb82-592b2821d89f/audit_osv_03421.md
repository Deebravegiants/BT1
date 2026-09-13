# [H] ALPINE-CVE-2026-11586

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11586
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11586
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.16.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.16.0 <8.21.0-r0

## Details
By default, curl automatically responds to WebSocket PING frames. Because curl
lacks an upper bound on memory allocation for unacknowledged frames, a
malicious server can exhaust all available memory by flooding curl with rapid,
sequential PING messages.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11586
