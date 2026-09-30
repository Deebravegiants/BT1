# [M] ALPINE-CVE-2022-0396

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-0396
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0396
Type: osv

## Affected
- Alpine:v3.12: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.13: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.14: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.15: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.16: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.17: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.18: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.19: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.20: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.21: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.22: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.23: `bind` — affected >=9.16.11 <9.16.27-r0
- Alpine:v3.24: `bind` — affected >=9.16.11 <9.16.27-r0

## Details
BIND 9.16.11 -> 9.16.26, 9.17.0 -> 9.18.0 and versions 9.16.11-S1 -> 9.16.26-S1 of the BIND Supported Preview Edition. Specifically crafted TCP streams can cause connections to BIND to remain in CLOSE_WAIT status for an indefinite period of time, even after the client has terminated the connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0396
