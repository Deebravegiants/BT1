# [M] ALPINE-CVE-2025-64506

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-64506
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-64506
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.6.0 <1.6.53-r0
- Alpine:v3.21: `libpng` — affected >=1.6.0 <1.6.53-r0
- Alpine:v3.22: `libpng` — affected >=1.6.0 <1.6.51-r0
- Alpine:v3.23: `libpng` — affected >=1.6.0 <1.6.51-r0
- Alpine:v3.24: `libpng` — affected >=1.6.0 <1.6.51-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From version 1.6.0 to before 1.6.51, a heap buffer over-read vulnerability exists in libpng's png_write_image_8bit function when processing 8-bit images through the simplified write API with convert_to_8bit enabled. The vulnerability affects 8-bit grayscale+alpha, RGB/RGBA, and images with incomplete row data. A conditional guard incorrectly allows 8-bit input to enter code expecting 16-bit input, causing reads up to 2 bytes beyond allocated buffer boundaries. This issue has been patched in version 1.6.51.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-64506
