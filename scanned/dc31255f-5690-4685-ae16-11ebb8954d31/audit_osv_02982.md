# [H] ALPINE-CVE-2024-12705

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-12705
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12705
Type: osv

## Affected
- Alpine:v3.18: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.19: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.22: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.23: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.24: `bind` — affected >=0 <9.18.33-r0

## Details
Clients using DNS-over-HTTPS (DoH) can exhaust a DNS resolver's CPU and/or memory by flooding it with crafted valid or invalid HTTP/2 traffic.
This issue affects BIND 9 versions 9.18.0 through 9.18.32, 9.20.0 through 9.20.4, 9.21.0 through 9.21.3, and 9.18.11-S1 through 9.18.32-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12705
