# [H] ALPINE-CVE-2016-5314

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5314
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5314
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
Buffer overflow in the PixarLogDecode function in tif_pixarlog.c in LibTIFF 4.0.6 and earlier allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted TIFF image, as demonstrated by overwriting the vgetparent function pointer with rgb2ycbcr.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5314
