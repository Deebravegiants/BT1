# [H] ALPINE-CVE-2019-16866

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-16866
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-16866
Type: osv

## Affected
- Alpine:v3.10: `unbound` — affected >=0 <1.9.1-r3
- Alpine:v3.11: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.12: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.13: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.14: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.15: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.16: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.17: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.18: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.19: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.20: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.21: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.22: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.23: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.9.4-r0
- Alpine:v3.8: `unbound` — affected >=0 <1.7.3-r1
- Alpine:v3.9: `unbound` — affected >=0 <1.8.3-r2

## Details
Unbound before 1.9.4 accesses uninitialized memory, which allows remote attackers to trigger a crash via a crafted NOTIFY query. The source IP address of the query must match an access-control rule.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-16866
