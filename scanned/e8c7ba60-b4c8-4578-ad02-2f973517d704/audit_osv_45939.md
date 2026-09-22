# [M] JLSEC-2026-498

## Summary
Severity: Medium
Advisory: JLSEC-2026-498
Ecosystem: Julia
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/JLSEC-2026-498
Type: osv

## Affected
- Julia: `libpng_jll` — affected >=0 <1.6.57+0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From 1.0.9 to before 1.6.57, passing a pointer obtained from `png_get_PLTE`, `png_get_tRNS`, or `png_get_hIST` back into the corresponding setter on the same `png_struct/png_info` pair causes the setter to read from freed memory and copy its contents into the replacement buffer. The setter frees the internal buffer before copying from the caller-supplied pointer, which now dangles. The freed region may contain stale data (producing silently corrupted chunk metadata) or data from subsequent heap allocations (leaking unrelated heap contents into the chunk struct). This vulnerability is fixed in 1.6.57.

## References
- https://github.com/pnggroup/libpng/commit/398cbe3df03f4e11bb031e07f416dfdde3684e8a
- https://github.com/pnggroup/libpng/commit/55d20aaa322c9274491cda82c5cd4f99b48c6bcc
- https://github.com/pnggroup/libpng/issues/836
- https://github.com/pnggroup/libpng/issues/837
- https://github.com/pnggroup/libpng/security/advisories/GHSA-6fr7-g8h7-v645
- https://lists.debian.org/debian-lts-announce/2026/05/msg00017.html
