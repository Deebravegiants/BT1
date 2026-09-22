# [M] ALPINE-CVE-2022-48281

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-48281
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-48281
Type: osv

## Affected
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r2
- Alpine:v3.18: `tiff` — affected >=0 <4.5.0-r3
- Alpine:v3.19: `tiff` — affected >=0 <4.5.0-r3
- Alpine:v3.20: `tiff` — affected >=0 <4.5.0-r3
- Alpine:v3.21: `tiff` — affected >=0 <4.5.0-r3
- Alpine:v3.22: `tiff` — affected >=0 <4.5.0-r3
- Alpine:v3.23: `tiff` — affected >=0 <4.5.0-r3
- Alpine:v3.24: `tiff` — affected >=0 <4.5.0-r3

## Details
processCropSelections in tools/tiffcrop.c in LibTIFF through 4.5.0 has a heap-based buffer overflow (e.g., "WRITE of size 307203") via a crafted TIFF image.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-48281
