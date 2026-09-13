# [C] ALPINE-CVE-2024-25176

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-25176
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-25176
Type: osv

## Affected
- Alpine:v3.19: `luajit` — affected >=0 <2.1_p20240815-r1
- Alpine:v3.20: `luajit` — affected >=0 <2.1_p20240815-r1
- Alpine:v3.21: `luajit` — affected >=0 <2.1_p20240815-r1
- Alpine:v3.22: `luajit` — affected >=0 <2.1_p20240815-r1
- Alpine:v3.23: `luajit` — affected >=0 <2.1_p20240815-r1
- Alpine:v3.24: `luajit` — affected >=0 <2.1_p20240815-r1

## Details
LuaJIT through 2.1 and OpenRusty luajit2 before v2.1-20240626 have a stack-buffer-overflow in lj_strfmt_wfnum in lj_strfmt_num.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-25176
