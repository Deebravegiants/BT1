# [M] ALPINE-CVE-2017-7593

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7593
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7593
Type: osv

## Affected
- Alpine:v3.10: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.11: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.12: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.13: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.14: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.15: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.16: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.17: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.18: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.19: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.20: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.21: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.22: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.23: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.24: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.5: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.6: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.7: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.8: `tiff` — affected >=0 <4.0.7-r2
- Alpine:v3.9: `tiff` — affected >=0 <4.0.7-r2

## Details
tif_read.c in LibTIFF 4.0.7 does not ensure that tif_rawdata is properly initialized, which might allow remote attackers to obtain sensitive information from process memory via a crafted image.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7593
