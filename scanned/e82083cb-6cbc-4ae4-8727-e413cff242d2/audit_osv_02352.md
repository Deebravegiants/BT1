# [C] ALPINE-CVE-2021-46461

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-46461
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-46461
Type: osv

## Affected
- Alpine:v3.16: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.17: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.18: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.19: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.20: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.21: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.22: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.23: `nginx` — affected >=0 <1.20.2-r2
- Alpine:v3.24: `nginx` — affected >=0 <1.20.2-r2

## Details
njs through 0.7.0, used in NGINX, was discovered to contain an out-of-bounds array access via njs_vmcode_typeof in /src/njs_vmcode.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-46461
