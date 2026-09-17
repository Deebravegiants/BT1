# [H] ALPINE-CVE-2018-1000222

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000222
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000222
Type: osv

## Affected
- Alpine:v3.10: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.11: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.12: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.13: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.14: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.15: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.16: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.17: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.18: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.19: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.20: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.21: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.22: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.23: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.24: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.5: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.6: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.7: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.8: `gd` — affected >=0 <2.2.5-r1
- Alpine:v3.9: `gd` — affected >=0 <2.2.5-r1

## Details
Libgd version 2.2.5 contains a Double Free Vulnerability vulnerability in gdImageBmpPtr Function that can result in Remote Code Execution . This attack appear to be exploitable via Specially Crafted Jpeg Image can trigger double free. This vulnerability appears to have been fixed in after commit ac16bdf2d41724b5a65255d4c28fb0ec46bc42f5.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000222
