# [H] ALPINE-CVE-2016-9453

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9453
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9453
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
The t2p_readwrite_pdf_image_tile function in LibTIFF allows remote attackers to cause a denial of service (out-of-bounds write and crash) or possibly execute arbitrary code via a JPEG file with a TIFFTAG_JPEGTABLES of length one.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9453
