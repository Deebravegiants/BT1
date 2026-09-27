# [M] ALPINE-CVE-2020-8624

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8624
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8624
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.11: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.12: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.13: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.14: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.15: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.16: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.17: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.18: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.19: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.20: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.21: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.22: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.23: `bind` — affected >=9.9.12 <9.16.6-r0
- Alpine:v3.24: `bind` — affected >=9.9.12 <9.16.6-r0

## Details
In BIND 9.9.12 -> 9.9.13, 9.10.7 -> 9.10.8, 9.11.3 -> 9.11.21, 9.12.1 -> 9.16.5, 9.17.0 -> 9.17.3, also affects 9.9.12-S1 -> 9.9.13-S1, 9.11.3-S1 -> 9.11.21-S1 of the BIND 9 Supported Preview Edition, An attacker who has been granted privileges to change a specific subset of the zone's content could abuse these unintended additional privileges to update other contents of the zone.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8624
