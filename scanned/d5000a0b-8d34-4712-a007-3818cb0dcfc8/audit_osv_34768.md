# [H] LIBPNG is vulnerable to a buffer overflow in `png_image_read_composite` via incorrect palette premultiplication

## Summary
Severity: High
Advisory: CVE-2025-64720
Aliases: A-463995203, ASB-A-463995203, GHSA-hfc7-ph9c-wcww
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-64720
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From version 1.6.0 to before 1.6.51, an out-of-bounds read vulnerability exists in png_image_read_composite when processing palette images with PNG_FLAG_OPTIMIZE_ALPHA enabled. The palette compositing code in png_init_read_transformations incorrectly applies background compositing during premultiplication, violating the invariant component ≤ alpha × 257 required by the simplified PNG API. This issue has been patched in version 1.6.51.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64720.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-hfc7-ph9c-wcww
- https://nvd.nist.gov/vuln/detail/CVE-2025-64720
- https://github.com/pnggroup/libpng/issues/686
- https://github.com/pnggroup/libpng/commit/08da33b4c88cfcd36e5a706558a8d7e0e4773643
- https://github.com/pnggroup/libpng/pull/751
