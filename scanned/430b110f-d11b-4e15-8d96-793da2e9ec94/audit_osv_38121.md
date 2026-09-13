# [M] LIBPNG has a yse-after-free in png_set_PLTE, png_set_tRNS and png_set_hIST leading to corrupted chunk data and potential heap information disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-34757
Aliases: GHSA-6fr7-g8h7-v645
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-34757
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From 1.0.9 to before 1.6.57, passing a pointer obtained from png_get_PLTE, png_get_tRNS, or png_get_hIST back into the corresponding setter on the same png_struct/png_info pair causes the setter to read from freed memory and copy its contents into the replacement buffer. The setter frees the internal buffer before copying from the caller-supplied pointer, which now dangles. The freed region may contain stale data (producing silently corrupted chunk metadata) or data from subsequent heap allocations (leaking unrelated heap contents into the chunk struct). This vulnerability is fixed in 1.6.57.

## References
- https://lists.debian.org/debian-lts-announce/2026/05/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34757.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-6fr7-g8h7-v645
- https://nvd.nist.gov/vuln/detail/CVE-2026-34757
- https://github.com/pnggroup/libpng/issues/836
- https://github.com/pnggroup/libpng/issues/837
- https://github.com/pnggroup/libpng/commit/398cbe3df03f4e11bb031e07f416dfdde3684e8a
- https://github.com/pnggroup/libpng/commit/55d20aaa322c9274491cda82c5cd4f99b48c6bcc
