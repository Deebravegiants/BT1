# [H] ALPINE-CVE-2019-6706

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6706
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6706
Type: osv

## Affected
- Alpine:v3.10: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.11: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.12: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.13: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.14: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.15: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.16: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.17: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.18: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.19: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.20: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.21: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.22: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.23: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.24: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.6: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.7: `lua5.3` — affected >=0 <5.3.5-r0
- Alpine:v3.8: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.9: `lua5.3` — affected >=0 <5.3.5-r2
- Alpine:v3.14: `lua5.4` — affected >=0 <5.3.5-r2
- Alpine:v3.15: `lua5.4` — affected >=0 <5.3.5-r2
- Alpine:v3.16: `lua5.4` — affected >=0 <5.3.5-r2
- Alpine:v3.17: `lua5.4` — affected >=0 <5.3.5-r2
- Alpine:v3.18: `lua5.4` — affected >=0 <5.3.5-r2
- Alpine:v3.19: `lua5.4` — affected >=0 <5.3.5-r2

## Details
Lua 5.3.5 has a use-after-free in lua_upvaluejoin in lapi.c. For example, a crash outcome might be achieved by an attacker who is able to trigger a debug.upvaluejoin call in which the arguments have certain relationships.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6706
