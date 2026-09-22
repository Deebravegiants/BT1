# [M] ALPINE-CVE-2022-3598

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-3598
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3598
Type: osv

## Affected
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r2
- Alpine:v3.18: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.5.0-r0

## Details
LibTIFF 4.4.0 has an out-of-bounds write in extractContigSamplesShifted24bits in tools/tiffcrop.c:3604, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit cfbb883b.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3598
