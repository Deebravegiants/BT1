# [M] ALPINE-CVE-2023-5680

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-5680
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5680
Type: osv

## Affected
- Alpine:v3.16: `bind` — affected >=0 <9.16.48-r0
- Alpine:v3.17: `bind` — affected >=0 <9.18.24-r0
- Alpine:v3.18: `bind` — affected >=0 <9.18.24-r0
- Alpine:v3.19: `bind` — affected >=0 <9.18.24-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.24-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.24-r0
- Alpine:v3.22: `bind` — affected >=0 <9.18.24-r0
- Alpine:v3.23: `bind` — affected >=0 <9.18.24-r0
- Alpine:v3.24: `bind` — affected >=0 <9.18.24-r0

## Details
If a resolver cache has a very large number of ECS records stored for the same name, the process of cleaning the cache database node for this name can significantly impair query performance. 
This issue affects BIND 9 versions 9.11.3-S1 through 9.11.37-S1, 9.16.8-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5680
