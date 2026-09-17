# [M] ALPINE-CVE-2023-0799

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-0799
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0799
Type: osv

## Affected
- Alpine:v3.15: `tiff` — affected >=0 <4.4.0-r2
- Alpine:v3.16: `tiff` — affected >=0 <4.4.0-r2
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r3
- Alpine:v3.18: `tiff` — affected >=0 <4.5.0-r5
- Alpine:v3.19: `tiff` — affected >=0 <4.5.0-r5
- Alpine:v3.20: `tiff` — affected >=0 <4.5.0-r5
- Alpine:v3.21: `tiff` — affected >=0 <4.5.0-r5
- Alpine:v3.22: `tiff` — affected >=0 <4.5.0-r5
- Alpine:v3.23: `tiff` — affected >=0 <4.5.0-r5
- Alpine:v3.24: `tiff` — affected >=0 <4.5.0-r5

## Details
LibTIFF 4.4.0 has an out-of-bounds read in tiffcrop in tools/tiffcrop.c:3701, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit afaabc3e.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0799
