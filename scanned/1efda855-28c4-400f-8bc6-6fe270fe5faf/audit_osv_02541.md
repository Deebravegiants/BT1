# [M] ALPINE-CVE-2022-2953

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-2953
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2953
Type: osv

## Affected
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.5.0-r0

## Details
LibTIFF 4.4.0 has an out-of-bounds read in extractImageSection in tools/tiffcrop.c:6905, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 48d6ece8.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2953
