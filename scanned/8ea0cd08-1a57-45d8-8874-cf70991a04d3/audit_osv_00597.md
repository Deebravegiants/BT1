# [M] ALPINE-CVE-2017-18013

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-18013
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-18013
Type: osv

## Affected
- Alpine:v3.10: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.11: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.12: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.13: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.14: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.15: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.16: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.17: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.4: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.5: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.6: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.7: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.8: `tiff` — affected >=0 <4.0.9-r1
- Alpine:v3.9: `tiff` — affected >=0 <4.0.9-r1

## Details
In LibTIFF 4.0.9, there is a Null-Pointer Dereference in the tif_print.c TIFFPrintDirectory function, as demonstrated by a tiffinfo crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-18013
