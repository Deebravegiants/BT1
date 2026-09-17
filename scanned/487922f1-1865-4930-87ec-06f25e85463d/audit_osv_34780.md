# [H] LIBPNG is vulnerable to a heap buffer overflow in `png_combine_row` triggered via `png_image_finish_read`

## Summary
Severity: High
Advisory: CVE-2025-65018
Aliases: A-463998243, ASB-A-463998243, GHSA-7wv6-48j4-hj3g
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65018
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From version 1.6.0 to before 1.6.51, there is a heap buffer overflow vulnerability in the libpng simplified API function png_image_finish_read when processing 16-bit interlaced PNGs with 8-bit output format. Attacker-crafted interlaced PNG files cause heap writes beyond allocated buffer bounds. This issue has been patched in version 1.6.51.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65018.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-7wv6-48j4-hj3g
- https://nvd.nist.gov/vuln/detail/CVE-2025-65018
- https://github.com/pnggroup/libpng/issues/755
- https://github.com/pnggroup/libpng/commit/16b5e3823918840aae65c0a6da57c78a5a496a4d
- https://github.com/pnggroup/libpng/commit/218612ddd6b17944e21eda56caf8b4bf7779d1ea
- https://github.com/pnggroup/libpng/pull/757
