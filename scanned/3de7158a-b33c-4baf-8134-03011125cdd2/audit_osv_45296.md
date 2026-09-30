# [M] LIBPNG is a reference library for use in applications that read, create, and manipulate PNG...

## Summary
Severity: Medium
Advisory: JLSEC-2025-328
Ecosystem: Julia
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/JLSEC-2025-328
Type: osv

## Affected
- Julia: `libpng_jll` — affected >=0 <1.6.51+0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. Prior to version 1.6.51, a heap buffer over-read vulnerability exists in libpng's `png_do_quantize` function when processing PNG files with malformed palette indices. The vulnerability occurs when `palette_lookup` array bounds are not validated against externally-supplied image data, allowing an attacker to craft a PNG file with out-of-range palette indices that trigger out-of-bounds memory access. This issue has been patched in version 1.6.51.

## References
- https://github.com/pnggroup/libpng/commit/6a528eb5fd0dd7f6de1c39d30de0e41473431c37
- https://github.com/pnggroup/libpng/pull/748
- https://github.com/pnggroup/libpng/security/advisories/GHSA-4952-h5wq-4m42
