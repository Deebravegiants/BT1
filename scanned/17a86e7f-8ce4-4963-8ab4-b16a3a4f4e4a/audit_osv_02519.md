# [M] ALPINE-CVE-2022-2795

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-2795
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2795
Type: osv

## Affected
- Alpine:v3.13: `bind` — affected >=9.0.0 <9.16.33-r0
- Alpine:v3.14: `bind` — affected >=9.0.0 <9.16.33-r0
- Alpine:v3.15: `bind` — affected >=9.0.0 <9.16.33-r0
- Alpine:v3.16: `bind` — affected >=9.0.0 <9.16.33-r0
- Alpine:v3.17: `bind` — affected >=9.0.0 <9.18.7-r0
- Alpine:v3.18: `bind` — affected >=9.0.0 <9.18.7-r0
- Alpine:v3.19: `bind` — affected >=9.0.0 <9.18.7-r0
- Alpine:v3.20: `bind` — affected >=9.0.0 <9.18.7-r0
- Alpine:v3.21: `bind` — affected >=9.0.0 <9.18.7-r0
- Alpine:v3.22: `bind` — affected >=9.0.0 <9.18.7-r0
- Alpine:v3.23: `bind` — affected >=9.0.0 <9.18.7-r0
- Alpine:v3.24: `bind` — affected >=9.0.0 <9.18.7-r0

## Details
By flooding the target resolver with queries exploiting this flaw an attacker can significantly impair the resolver's performance, effectively denying legitimate clients access to the DNS resolution service.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2795
