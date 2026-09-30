# [M] ALPINE-CVE-2026-5950

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-5950
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5950
Type: osv

## Affected
- Alpine:v3.20: `bind` — affected >=9.18.36 <9.18.49-r0
- Alpine:v3.21: `bind` — affected >=9.18.36 <9.18.49-r0
- Alpine:v3.22: `bind` — affected >=9.18.36 <9.20.23-r0
- Alpine:v3.23: `bind` — affected >=9.18.36 <9.20.23-r0
- Alpine:v3.24: `bind` — affected >=9.18.36 <9.20.23-r0

## Details
An unbounded resend loop vulnerability exists in the BIND 9 resolver state machine during bad-server handling, enabling a remote unauthenticated attacker to cause severe resource exhaustion by sending queries that trigger specific retry conditions.
This issue affects BIND 9 versions 9.18.36 through 9.18.48, 9.20.8 through 9.20.22, 9.21.7 through 9.21.21, 9.18.36-S1 through 9.18.48-S1, and 9.20.9-S1 through 9.20.22-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5950
