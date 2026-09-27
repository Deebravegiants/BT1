# [M] ALPINE-CVE-2022-2521

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-2521
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2521
Type: osv

## Affected
- Alpine:v3.15: `tiff` — affected >=0 <4.4.0-r3
- Alpine:v3.16: `tiff` — affected >=0 <4.4.0-r3
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.4.0-r1

## Details
It was found in libtiff 4.4.0rc1 that there is an invalid pointer free operation in TIFFClose() at tif_close.c:131 called by tiffcrop.c:2522 that can cause a program crash and denial of service while processing crafted input.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2521
