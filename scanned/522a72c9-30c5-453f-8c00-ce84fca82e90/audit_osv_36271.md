# [M] LIBPNG has a heap buffer over-read in png_image_read_direct_scaled (regression from CVE-2025-65018 fix)

## Summary
Severity: Medium
Advisory: CVE-2026-22695
Aliases: GHSA-mmq5-27w3-rxpp
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22695
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From 1.6.51 to 1.6.53, there is a heap buffer over-read in the libpng simplified API function png_image_finish_read when processing interlaced 16-bit PNGs with 8-bit output format and non-minimal row stride. This is a regression introduced by the fix for CVE-2025-65018. This vulnerability is fixed in 1.6.54.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22695.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-mmq5-27w3-rxpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-22695
- https://github.com/pnggroup/libpng/issues/778
- https://github.com/pnggroup/libpng/commit/218612ddd6b17944e21eda56caf8b4bf7779d1ea
- https://github.com/pnggroup/libpng/commit/e4f7ad4ea2
