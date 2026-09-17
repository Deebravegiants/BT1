# [M] ALPINE-CVE-2018-5736

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5736
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5736
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.11: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.12: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.13: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.14: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.15: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.16: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.17: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.18: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.19: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.20: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.21: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.22: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.23: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.24: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.8: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.9: `bind` — affected >=0 <9.12.1_p2-r0

## Details
An error in zone database reference counting can lead to an assertion failure if a server which is running an affected version of BIND attempts several transfers of a slave zone in quick succession. This defect could be deliberately exercised by an attacker who is permitted to cause a vulnerable server to initiate zone transfers (for example: by sending valid NOTIFY messages), causing the named process to exit after failing the assertion test. Affects BIND 9.12.0 and 9.12.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5736
