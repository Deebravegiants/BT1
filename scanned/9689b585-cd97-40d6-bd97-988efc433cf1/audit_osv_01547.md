# [C] ALPINE-CVE-2019-20367

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-20367
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20367
Type: osv

## Affected
- Alpine:v3.10: `libbsd` — affected >=0 <0.9.1-r1
- Alpine:v3.11: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.12: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.13: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.14: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.15: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.16: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.17: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.18: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.19: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.20: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.21: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.22: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.23: `libbsd` — affected >=0 <0.10.0-r0
- Alpine:v3.24: `libbsd` — affected >=0 <0.10.0-r0

## Details
nlist.c in libbsd before 0.10.0 has an out-of-bounds read during a comparison for a symbol name from the string table (strtab).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20367
