# [H] ALPINE-CVE-2025-65018

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-65018
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-65018
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.6.0 <1.6.53-r0
- Alpine:v3.21: `libpng` — affected >=1.6.0 <1.6.53-r0
- Alpine:v3.22: `libpng` — affected >=1.6.0 <1.6.51-r0
- Alpine:v3.23: `libpng` — affected >=1.6.0 <1.6.51-r0
- Alpine:v3.24: `libpng` — affected >=1.6.0 <1.6.51-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From version 1.6.0 to before 1.6.51, there is a heap buffer overflow vulnerability in the libpng simplified API function png_image_finish_read when processing 16-bit interlaced PNGs with 8-bit output format. Attacker-crafted interlaced PNG files cause heap writes beyond allocated buffer bounds. This issue has been patched in version 1.6.51.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-65018
