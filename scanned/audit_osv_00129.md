# [M] ALPINE-CVE-2016-5316

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-5316
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5316
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
Out-of-bounds read in the PixarLogCleanup function in tif_pixarlog.c in libtiff 4.0.6 and earlier allows remote attackers to crash the application by sending a crafted TIFF image to the rgb2ycbcr tool.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5316
