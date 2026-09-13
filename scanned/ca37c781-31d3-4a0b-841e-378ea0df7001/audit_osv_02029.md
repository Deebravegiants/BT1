# [H] ALPINE-CVE-2020-8621

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8621
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8621
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.11: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.12: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.13: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.14: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.15: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.16: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.17: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.18: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.19: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.20: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.21: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.22: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.23: `bind` — affected >=9.14.0 <9.16.6-r0
- Alpine:v3.24: `bind` — affected >=9.14.0 <9.16.6-r0

## Details
In BIND 9.14.0 -> 9.16.5, 9.17.0 -> 9.17.3, If a server is configured with both QNAME minimization and 'forward first' then an attacker who can send queries to it may be able to trigger the condition that will cause the server to crash. Servers that 'forward only' are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8621
