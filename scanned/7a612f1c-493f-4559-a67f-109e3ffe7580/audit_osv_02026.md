# [M] ALPINE-CVE-2020-8618

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8618
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8618
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.11: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.12: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.13: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.14: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.15: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.16: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.17: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.18: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.19: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.20: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.21: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.22: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.23: `bind` — affected >=9.16.0 <9.16.4-r0
- Alpine:v3.24: `bind` — affected >=9.16.0 <9.16.4-r0

## Details
An attacker who is permitted to send zone data to a server via zone transfer can exploit this to intentionally trigger the assertion failure with a specially constructed zone, denying service to clients.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8618
