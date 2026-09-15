# [M] ALPINE-CVE-2014-8127

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2014-8127
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2014-8127
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
LibTIFF 4.0.3 allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted TIFF image to the (1) checkInkNamesString function in tif_dir.c in the thumbnail tool, (2) compresscontig function in tiff2bw.c in the tiff2bw tool, (3) putcontig8bitCIELab function in tif_getimage.c in the tiff2rgba tool, LZWPreDecode function in tif_lzw.c in the (4) tiff2ps or (5) tiffdither tool, (6) NeXTDecode function in tif_next.c in the tiffmedian tool, or (7) TIFFWriteDirectoryTagLongLong8Array function in tif_dirwrite.c in the tiffset tool.

## References
- https://security.alpinelinux.org/vuln/CVE-2014-8127
