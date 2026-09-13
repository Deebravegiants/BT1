# [M] A flaw was found in tiffcrop, a program distributed by the libtiff package

## Summary
Severity: Medium
Advisory: JLSEC-2025-301
Ecosystem: Julia
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-301
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
A flaw was found in tiffcrop, a program distributed by the libtiff package. A specially crafted tiff file can lead to an out-of-bounds read in the extractImageSection function in `tools/tiffcrop.c`, resulting in a denial of service and limited information disclosure. This issue affects libtiff versions 4.x.

## References
- https://gitlab.com/libtiff/libtiff/-/issues/536
- https://gitlab.com/libtiff/libtiff/-/issues/536%2C
- https://gitlab.com/libtiff/libtiff/-/issues/537
- https://support.apple.com/kb/HT213844
