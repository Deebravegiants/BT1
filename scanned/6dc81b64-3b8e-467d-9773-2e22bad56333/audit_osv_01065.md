# [H] ALPINE-CVE-2018-18557

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-18557
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18557
Type: osv

## Affected
- Alpine:v3.10: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.11: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.12: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.13: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.14: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.15: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.16: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.17: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.18: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.6: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.7: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.8: `tiff` — affected >=0 <4.0.10-r0
- Alpine:v3.9: `tiff` — affected >=0 <4.0.10-r0

## Details
LibTIFF 3.9.3, 3.9.4, 3.9.5, 3.9.6, 3.9.7, 4.0.0alpha4, 4.0.0alpha5, 4.0.0alpha6, 4.0.0beta7, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.0.4, 4.0.4beta, 4.0.5, 4.0.6, 4.0.7, 4.0.8 and 4.0.9 (with JBIG enabled) decodes arbitrarily-sized JBIG into a buffer, ignoring the buffer size, which leads to a tif_jbig.c JBIGDecode out-of-bounds write.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18557
