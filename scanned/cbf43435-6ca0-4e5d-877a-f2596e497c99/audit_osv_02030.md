# [M] ALPINE-CVE-2020-8622

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8622
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8622
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.11: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.12: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.13: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.14: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.15: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.16: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.17: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.18: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.19: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.20: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.21: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.22: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.23: `bind` — affected >=9.0.0 <9.16.6-r0
- Alpine:v3.24: `bind` — affected >=9.0.0 <9.16.6-r0

## Details
In BIND 9.0.0 -> 9.11.21, 9.12.0 -> 9.16.5, 9.17.0 -> 9.17.3, also affects 9.9.3-S1 -> 9.11.21-S1 of the BIND 9 Supported Preview Edition, An attacker on the network path for a TSIG-signed request, or operating the server receiving the TSIG-signed request, could send a truncated response to that request, triggering an assertion failure, causing the server to exit. Alternately, an off-path attacker would have to correctly guess when a TSIG-signed request was sent, along with other characteristics of the packet and message, and spoof a truncated response to trigger an assertion failure, causing the server to exit.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8622
