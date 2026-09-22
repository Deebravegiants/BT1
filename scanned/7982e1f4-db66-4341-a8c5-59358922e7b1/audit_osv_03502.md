# [H] ALPINE-CVE-2026-22695

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-22695
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-22695
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.6.51 <1.6.54-r0
- Alpine:v3.21: `libpng` — affected >=1.6.51 <1.6.54-r0
- Alpine:v3.22: `libpng` — affected >=1.6.51 <1.6.54-r0
- Alpine:v3.23: `libpng` — affected >=1.6.51 <1.6.54-r0
- Alpine:v3.24: `libpng` — affected >=1.6.51 <1.6.54-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From 1.6.51 to 1.6.53, there is a heap buffer over-read in the libpng simplified API function png_image_finish_read when processing interlaced 16-bit PNGs with 8-bit output format and non-minimal row stride. This is a regression introduced by the fix for CVE-2025-65018. This vulnerability is fixed in 1.6.54.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-22695
