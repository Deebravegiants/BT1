# [H] JLSEC-2026-95

## Summary
Severity: High
Advisory: JLSEC-2026-95
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-95
Type: osv

## Affected
- Julia: `libpng_jll` — affected >=0 <1.6.56+0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. In versions 1.2.1 through 1.6.55, `png_set_tRNS` and `png_set_PLTE` each alias a heap-allocated buffer between `png_struct` and `png_info`, sharing a single allocation across two structs with independent lifetimes. The `trans_alpha` aliasing has been present since at least libpng 1.0, and the `palette` aliasing since at least 1.2.1. Both affect all prior release lines `png_set_tRNS` sets `png_ptr->trans_alpha = info_ptr->trans_alpha` (256-byte buffer) and `png_set_PLTE` sets `info_ptr->palette = png_ptr->palette` (768-byte buffer). In both cases, calling `png_free_data` (with `PNG_FREE_TRNS` or `PNG_FREE_PLTE`) frees the buffer through `info_ptr` while the corresponding `png_ptr` pointer remains dangling. Subsequent row-transform functions dereference and, in some code paths, write to the freed memory. A second call to `png_set_tRNS` or `png_set_PLTE` has the same effect, because both functions call `png_free_data` internally before reallocating the `info_ptr` buffer. Version 1.6.56 fixes the issue.

## References
- https://github.com/pnggroup/libpng/commit/23019269764e35ed8458e517f1897bd3c54820eb
- https://github.com/pnggroup/libpng/commit/7ea9eea884a2328cc7fdcb3c0c00246a50d90667
- https://github.com/pnggroup/libpng/commit/a3a21443ed12bfa1ef46fa0d4fb2b74a0fa34a25
- https://github.com/pnggroup/libpng/commit/c1b0318b393c90679e6fa5bc1d329fd5d5012ec1
- https://github.com/pnggroup/libpng/pull/824
- https://github.com/pnggroup/libpng/security/advisories/GHSA-m4pc-p4q3-4c7j
