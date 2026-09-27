# [M] ALPINE-CVE-2021-36411

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-36411
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-36411
Type: osv

## Affected
- Alpine:v3.14: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.15: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.16: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.17: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.18: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.19: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.20: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.21: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.22: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.23: `libde265` — affected >=0 <1.0.8-r2
- Alpine:v3.24: `libde265` — affected >=0 <1.0.8-r2

## Details
An issue has been found in libde265 v1.0.8 due to incorrect access control. A SEGV caused by a READ memory access in function derive_boundaryStrength of deblock.cc has occurred. The vulnerability causes a segmentation fault and application crash, which leads to remote denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-36411
