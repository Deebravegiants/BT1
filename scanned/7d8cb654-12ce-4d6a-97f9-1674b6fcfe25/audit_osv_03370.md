# [H] ALPINE-CVE-2025-64720

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-64720
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-64720
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.6.0 <1.6.53-r0
- Alpine:v3.21: `libpng` — affected >=1.6.0 <1.6.53-r0
- Alpine:v3.22: `libpng` — affected >=1.6.0 <1.6.51-r0
- Alpine:v3.23: `libpng` — affected >=1.6.0 <1.6.51-r0
- Alpine:v3.24: `libpng` — affected >=1.6.0 <1.6.51-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From version 1.6.0 to before 1.6.51, an out-of-bounds read vulnerability exists in png_image_read_composite when processing palette images with PNG_FLAG_OPTIMIZE_ALPHA enabled. The palette compositing code in png_init_read_transformations incorrectly applies background compositing during premultiplication, violating the invariant component ≤ alpha × 257 required by the simplified PNG API. This issue has been patched in version 1.6.51.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-64720
