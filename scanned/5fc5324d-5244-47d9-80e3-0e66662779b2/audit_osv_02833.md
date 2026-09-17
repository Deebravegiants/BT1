# [M] ALPINE-CVE-2023-33460

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-33460
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-33460
Type: osv

## Affected
- Alpine:v3.19: `yajl` — affected >=0 <2.1.0-r9
- Alpine:v3.20: `yajl` — affected >=0 <2.1.0-r9
- Alpine:v3.21: `yajl` — affected >=0 <2.1.0-r9
- Alpine:v3.22: `yajl` — affected >=0 <2.1.0-r9
- Alpine:v3.23: `yajl` — affected >=0 <2.1.0-r9
- Alpine:v3.24: `yajl` — affected >=0 <2.1.0-r9

## Details
There's a memory leak in yajl 2.1.0 with use of yajl_tree_parse function. which will cause out-of-memory in server and cause crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-33460
