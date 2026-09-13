# [H] ALPINE-CVE-2026-1519

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-1519
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-1519
Type: osv

## Affected
- Alpine:v3.20: `bind` — affected >=9.11.0 <9.18.47-r0
- Alpine:v3.21: `bind` — affected >=9.11.0 <9.18.47-r0
- Alpine:v3.22: `bind` — affected >=9.11.0 <9.20.21-r0
- Alpine:v3.23: `bind` — affected >=9.11.0 <9.20.21-r0
- Alpine:v3.24: `bind` — affected >=9.11.0 <9.20.21-r0

## Details
If a BIND resolver is performing DNSSEC validation and encounters a maliciously crafted zone, the resolver may consume excessive CPU. Authoritative-only servers are generally unaffected, although there are circumstances where authoritative servers may make recursive queries (see: https://kb.isc.org/docs/why-does-my-authoritative-server-make-recursive-queries).
This issue affects BIND 9 versions 9.11.0 through 9.16.50, 9.18.0 through 9.18.46, 9.20.0 through 9.20.20, 9.21.0 through 9.21.19, 9.11.3-S1 through 9.16.50-S1, 9.18.11-S1 through 9.18.46-S1, and 9.20.9-S1 through 9.20.20-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-1519
