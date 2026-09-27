# [H] ALPINE-CVE-2016-10165

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-10165
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10165
Type: osv

## Affected
- Alpine:v3.10: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.11: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.12: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.13: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.14: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.15: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.16: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.17: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.18: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.19: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.2: `lcms2` — affected >=0 <2.8-r0
- Alpine:v3.20: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.21: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.22: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.23: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.24: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.3: `lcms2` — affected >=0 <2.8-r0
- Alpine:v3.4: `lcms2` — affected >=0 <2.8-r0
- Alpine:v3.5: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.6: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.7: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.8: `lcms2` — affected >=0 <2.8-r1
- Alpine:v3.9: `lcms2` — affected >=0 <2.8-r1

## Details
The Type_MLU_Read function in cmstypes.c in Little CMS (aka lcms2) allows remote attackers to obtain sensitive information or cause a denial of service via an image with a crafted ICC profile, which triggers an out-of-bounds heap read.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10165
