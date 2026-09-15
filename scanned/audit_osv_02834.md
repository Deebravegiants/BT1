# [M] ALPINE-CVE-2023-33461

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-33461
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-33461
Type: osv

## Affected
- Alpine:v3.17: `iniparser` — affected >=0 <4.1-r2
- Alpine:v3.18: `iniparser` — affected >=0 <4.1-r3
- Alpine:v3.19: `iniparser` — affected >=0 <4.1-r3
- Alpine:v3.20: `iniparser` — affected >=0 <4.1-r3
- Alpine:v3.21: `iniparser` — affected >=0 <4.1-r3
- Alpine:v3.22: `iniparser` — affected >=0 <4.1-r3
- Alpine:v3.23: `iniparser` — affected >=0 <4.1-r3
- Alpine:v3.24: `iniparser` — affected >=0 <4.1-r3

## Details
iniparser v4.1 is vulnerable to NULL Pointer Dereference in function iniparser_getlongint which misses check NULL for function iniparser_getstring's return.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-33461
