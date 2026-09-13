# [M] ALPINE-CVE-2025-64505

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-64505
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-64505
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=0 <1.6.53-r0
- Alpine:v3.21: `libpng` — affected >=0 <1.6.53-r0
- Alpine:v3.22: `libpng` — affected >=0 <1.6.51-r0
- Alpine:v3.23: `libpng` — affected >=0 <1.6.51-r0
- Alpine:v3.24: `libpng` — affected >=0 <1.6.51-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. Prior to version 1.6.51, a heap buffer over-read vulnerability exists in libpng's png_do_quantize function when processing PNG files with malformed palette indices. The vulnerability occurs when palette_lookup array bounds are not validated against externally-supplied image data, allowing an attacker to craft a PNG file with out-of-range palette indices that trigger out-of-bounds memory access. This issue has been patched in version 1.6.51.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-64505
