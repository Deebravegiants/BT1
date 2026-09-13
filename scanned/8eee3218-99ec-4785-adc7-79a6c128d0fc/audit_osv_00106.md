# [H] ALPINE-CVE-2016-3658

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-3658
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3658
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
The TIFFWriteDirectoryTagLongLong8Array function in tif_dirwrite.c in the tiffset tool in LibTIFF 4.0.6 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) via vectors involving the ma variable.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3658
