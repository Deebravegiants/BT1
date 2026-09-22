# [H] JLSEC-2026-96

## Summary
Severity: High
Advisory: JLSEC-2026-96
Ecosystem: Julia
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-96
Type: osv

## Affected
- Julia: `libpng_jll` — affected >=0 <1.6.56+0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. In versions 1.6.36 through 1.6.55, an out-of-bounds read and write exists in libpng's ARM/AArch64 Neon-optimized palette expansion path. When expanding 8-bit paletted rows to RGB or RGBA, the Neon loop processes a final partial chunk without verifying that enough input pixels remain. Because the implementation works backward from the end of the row, the final iteration dereferences pointers before the start of the row buffer (OOB read) and writes expanded pixel data to the same underflowed positions (OOB write). This is reachable via normal decoding of attacker-controlled PNG input if Neon is enabled. Version 1.6.56 fixes the issue.

## References
- https://github.com/pnggroup/libpng/commit/7734cda20cf1236aef60f3bbd2267c97bbb40869
- https://github.com/pnggroup/libpng/commit/aba9f18eba870d14fb52c5ba5d73451349e339c3
- https://github.com/pnggroup/libpng/security/advisories/GHSA-wjr5-c57x-95m2
