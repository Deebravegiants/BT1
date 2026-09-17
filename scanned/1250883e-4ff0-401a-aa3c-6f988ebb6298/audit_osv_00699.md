# [H] ALPINE-CVE-2017-6363

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-6363
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6363
Type: osv

## Affected
- Alpine:v3.11: `gd` — affected >=0 <2.2.5-r4
- Alpine:v3.12: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.13: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.14: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.15: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.16: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.17: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.18: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.19: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.20: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.21: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.22: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.23: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.24: `gd` — affected >=0 <2.3.0-r0

## Details
In the GD Graphics Library (aka LibGD) through 2.2.5, there is a heap-based buffer over-read in tiffWriter in gd_tiff.c. NOTE: the vendor says "In my opinion this issue should not have a CVE, since the GD and GD2 formats are documented to be 'obsolete, and should only be used for development and testing purposes.'

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6363
