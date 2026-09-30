# [M] ALPINE-CVE-2018-7456

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-7456
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7456
Type: osv

## Affected
- Alpine:v3.10: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.11: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.12: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.13: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.14: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.15: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.16: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.17: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.18: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.19: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.20: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.21: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.22: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.23: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.24: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.4: `tiff` — affected >=0 <4.0.9-r3
- Alpine:v3.5: `tiff` — affected >=0 <4.0.9-r3
- Alpine:v3.6: `tiff` — affected >=0 <4.0.9-r3
- Alpine:v3.7: `tiff` — affected >=0 <4.0.9-r3
- Alpine:v3.8: `tiff` — affected >=0 <4.0.9-r4
- Alpine:v3.9: `tiff` — affected >=0 <4.0.9-r4

## Details
A NULL Pointer Dereference occurs in the function TIFFPrintDirectory in tif_print.c in LibTIFF 3.9.3, 3.9.4, 3.9.5, 3.9.6, 3.9.7, 4.0.0alpha4, 4.0.0alpha5, 4.0.0alpha6, 4.0.0beta7, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.0.4, 4.0.4beta, 4.0.5, 4.0.6, 4.0.7, 4.0.8 and 4.0.9 when using the tiffinfo tool to print crafted TIFF information, a different vulnerability than CVE-2017-18013. (This affects an earlier part of the TIFFPrintDirectory function that was not addressed by the CVE-2017-18013 patch.)

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7456
