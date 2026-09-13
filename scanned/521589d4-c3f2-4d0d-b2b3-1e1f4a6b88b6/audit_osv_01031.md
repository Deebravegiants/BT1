# [M] ALPINE-CVE-2018-16435

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-16435
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16435
Type: osv

## Affected
- Alpine:v3.10: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.11: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.12: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.13: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.14: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.15: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.16: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.17: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.18: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.19: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.20: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.21: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.22: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.23: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.24: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.8: `lcms2` — affected >=0 <2.9-r1
- Alpine:v3.9: `lcms2` — affected >=0 <2.9-r1

## Details
Little CMS (aka Little Color Management System) 2.9 has an integer overflow in the AllocateDataSet function in cmscgats.c, leading to a heap-based buffer overflow in the SetData function via a crafted file in the second argument to cmsIT8LoadFromFile.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16435
