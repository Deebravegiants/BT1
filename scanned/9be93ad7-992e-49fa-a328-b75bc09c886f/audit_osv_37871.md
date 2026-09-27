# [H] LIBPNG has ARM NEON Palette Expansion Out-of-Bounds Read on AArch64

## Summary
Severity: High
Advisory: CVE-2026-33636
Aliases: A-496616027, ASB-A-496616027, GHSA-wjr5-c57x-95m2
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33636
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. In versions 1.6.36 through 1.6.55, an out-of-bounds read and write exists in libpng's ARM/AArch64 Neon-optimized palette expansion path. When expanding 8-bit paletted rows to RGB or RGBA, the Neon loop processes a final partial chunk without verifying that enough input pixels remain. Because the implementation works backward from the end of the row, the final iteration dereferences pointers before the start of the row buffer (OOB read) and writes expanded pixel data to the same underflowed positions (OOB write). This is reachable via normal decoding of attacker-controlled PNG input if Neon is enabled. Version 1.6.56 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33636.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-wjr5-c57x-95m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33636
- https://github.com/pnggroup/libpng/commit/7734cda20cf1236aef60f3bbd2267c97bbb40869
- https://github.com/pnggroup/libpng/commit/aba9f18eba870d14fb52c5ba5d73451349e339c3
