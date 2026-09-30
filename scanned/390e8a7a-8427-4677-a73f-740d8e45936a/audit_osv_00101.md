# [H] ALPINE-CVE-2016-3621

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-3621
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3621
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
The LZWEncode function in tif_lzw.c in the bmp2tiff tool in LibTIFF 4.0.6 and earlier, when the "-c lzw" option is used, allows remote attackers to cause a denial of service (buffer over-read) via a crafted BMP image.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3621
