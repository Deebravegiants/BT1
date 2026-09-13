# [C] ALPINE-CVE-2022-28805

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-28805
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-28805
Type: osv

## Affected
- Alpine:v3.14: `lua5.4` — affected >=0 <5.4.3-r1
- Alpine:v3.15: `lua5.4` — affected >=0 <5.4.3-r1
- Alpine:v3.16: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.17: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.18: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.19: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.20: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.21: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.22: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.23: `lua5.4` — affected >=0 <5.4.4-r4
- Alpine:v3.24: `lua5.4` — affected >=0 <5.4.4-r4

## Details
singlevar in lparser.c in Lua from (including) 5.4.0 up to (excluding) 5.4.4 lacks a certain luaK_exp2anyregup call, leading to a heap-based buffer over-read that might affect a system that compiles untrusted Lua code.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-28805
