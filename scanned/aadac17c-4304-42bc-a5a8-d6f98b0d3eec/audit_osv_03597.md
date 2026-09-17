# [H] ALPINE-CVE-2026-33416

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-33416
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33416
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.2.1 <1.6.56-r0
- Alpine:v3.21: `libpng` — affected >=1.2.1 <1.6.56-r0
- Alpine:v3.22: `libpng` — affected >=1.2.1 <1.6.56-r0
- Alpine:v3.23: `libpng` — affected >=1.2.1 <1.6.56-r0
- Alpine:v3.24: `libpng` — affected >=1.2.1 <1.6.56-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. In versions 1.2.1 through 1.6.55, `png_set_tRNS` and `png_set_PLTE` each alias a heap-allocated buffer between `png_struct` and `png_info`, sharing a single allocation across two structs with independent lifetimes. The `trans_alpha` aliasing has been present since at least libpng 1.0, and the `palette` aliasing since at least 1.2.1. Both affect all prior release lines `png_set_tRNS` sets `png_ptr->trans_alpha = info_ptr->trans_alpha` (256-byte buffer) and `png_set_PLTE` sets `info_ptr->palette = png_ptr->palette` (768-byte buffer). In both cases, calling `png_free_data` (with `PNG_FREE_TRNS` or `PNG_FREE_PLTE`) frees the buffer through `info_ptr` while the corresponding `png_ptr` pointer remains dangling. Subsequent row-transform functions dereference and, in some code paths, write to the freed memory. A second call to `png_set_tRNS` or `png_set_PLTE` has the same effect, because both functions call `png_free_data` internally before reallocating the `info_ptr` buffer. Version 1.6.56 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33416
