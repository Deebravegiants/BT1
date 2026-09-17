# [H] ALPINE-CVE-2026-25646

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-25646
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-25646
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=0 <1.6.55-r0
- Alpine:v3.21: `libpng` — affected >=0 <1.6.55-r0
- Alpine:v3.22: `libpng` — affected >=0 <1.6.55-r0
- Alpine:v3.23: `libpng` — affected >=0 <1.6.55-r0
- Alpine:v3.24: `libpng` — affected >=0 <1.6.55-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. Prior to 1.6.55, an out-of-bounds read vulnerability exists in the png_set_quantize() API function. When the function is called with no histogram and the number of colors in the palette is more than twice the maximum supported by the user's display, certain palettes will cause the function to enter into an infinite loop that reads past the end of an internal heap-allocated buffer. The images that trigger this vulnerability are valid per the PNG specification. This vulnerability is fixed in 1.6.55.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-25646
