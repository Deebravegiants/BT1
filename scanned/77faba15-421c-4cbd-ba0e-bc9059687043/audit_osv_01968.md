# [M] ALPINE-CVE-2020-35521

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-35521
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35521
Type: osv

## Affected
- Alpine:v3.13: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.14: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.15: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.16: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.17: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.18: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.2.0-r0

## Details
A flaw was found in libtiff. Due to a memory allocation failure in tif_read.c, a crafted TIFF file can lead to an abort, resulting in denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35521
