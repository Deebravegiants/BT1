# [M] LIBPNG is vulnerable to a heap buffer overflow in `png_do_quantize` via malformed palette index

## Summary
Severity: Medium
Advisory: CVE-2025-64505
Aliases: A-463980379, ASB-A-463980379, GHSA-4952-h5wq-4m42
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-64505
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. Prior to version 1.6.51, a heap buffer over-read vulnerability exists in libpng's png_do_quantize function when processing PNG files with malformed palette indices. The vulnerability occurs when palette_lookup array bounds are not validated against externally-supplied image data, allowing an attacker to craft a PNG file with out-of-range palette indices that trigger out-of-bounds memory access. This issue has been patched in version 1.6.51.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64505.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-4952-h5wq-4m42
- https://nvd.nist.gov/vuln/detail/CVE-2025-64505
- https://github.com/pnggroup/libpng/commit/6a528eb5fd0dd7f6de1c39d30de0e41473431c37
- https://github.com/pnggroup/libpng/pull/748
