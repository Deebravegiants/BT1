# [H] ALPINE-CVE-2026-22801

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-22801
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-22801
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.6.26 <1.6.54-r0
- Alpine:v3.21: `libpng` — affected >=1.6.26 <1.6.54-r0
- Alpine:v3.22: `libpng` — affected >=1.6.26 <1.6.54-r0
- Alpine:v3.23: `libpng` — affected >=1.6.26 <1.6.54-r0
- Alpine:v3.24: `libpng` — affected >=1.6.26 <1.6.54-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From 1.6.26 to 1.6.53, there is an integer truncation in the libpng simplified write API functions png_write_image_16bit and png_write_image_8bit causes heap buffer over-read when the caller provides a negative row stride (for bottom-up image layouts) or a stride exceeding 65535 bytes. The bug was introduced in libpng 1.6.26 (October 2016) by casts added to silence compiler warnings on 16-bit systems. This vulnerability is fixed in 1.6.54.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-22801
