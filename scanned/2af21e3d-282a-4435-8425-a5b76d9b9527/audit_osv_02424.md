# [M] ALPINE-CVE-2022-22844

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-22844
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-22844
Type: osv

## Affected
- Alpine:v3.13: `tiff` — affected >=0 <4.3.0-r0
- Alpine:v3.14: `tiff` — affected >=0 <4.3.0-r0
- Alpine:v3.15: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.16: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.17: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.3.0-r1

## Details
LibTIFF 4.3.0 has an out-of-bounds read in _TIFFmemcpy in tif_unix.c in certain situations involving a custom tag and 0x0200 as the second word of the DE field.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-22844
