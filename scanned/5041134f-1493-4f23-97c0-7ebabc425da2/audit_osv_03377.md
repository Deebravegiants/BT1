# [H] ALPINE-CVE-2025-66293

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-66293
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-66293
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=0 <1.6.53-r0
- Alpine:v3.21: `libpng` — affected >=0 <1.6.53-r0
- Alpine:v3.22: `libpng` — affected >=0 <1.6.53-r0
- Alpine:v3.23: `libpng` — affected >=0 <1.6.53-r0
- Alpine:v3.24: `libpng` — affected >=0 <1.6.53-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. Prior to 1.6.52, an out-of-bounds read vulnerability in libpng's simplified API allows reading up to 1012 bytes beyond the png_sRGB_base[512] array when processing valid palette PNG images with partial transparency and gamma correction. The PNG files that trigger this vulnerability are valid per the PNG specification; the bug is in libpng's internal state management. Upgrade to libpng 1.6.52 or later.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-66293
