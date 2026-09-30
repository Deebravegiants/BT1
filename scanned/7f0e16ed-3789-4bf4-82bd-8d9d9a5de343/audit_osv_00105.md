# [M] ALPINE-CVE-2016-3625

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-3625
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3625
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
tif_read.c in the tiff2bw tool in LibTIFF 4.0.6 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TIFF image.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3625
