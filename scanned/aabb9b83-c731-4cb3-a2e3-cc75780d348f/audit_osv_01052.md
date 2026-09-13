# [H] ALPINE-CVE-2018-17101

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-17101
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-17101
Type: osv

## Affected
- Alpine:v3.10: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.11: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.12: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.13: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.14: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.15: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.16: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.17: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.18: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.19: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.20: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.21: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.22: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.23: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.24: `tiff` — affected >=0 <4.0.9-r8
- Alpine:v3.5: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.6: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.7: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.8: `tiff` — affected >=0 <4.0.9-r7
- Alpine:v3.9: `tiff` — affected >=0 <4.0.9-r8

## Details
An issue was discovered in LibTIFF 4.0.9. There are two out-of-bounds writes in cpTags in tools/tiff2bw.c and tools/pal2rgb.c, which can cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-17101
