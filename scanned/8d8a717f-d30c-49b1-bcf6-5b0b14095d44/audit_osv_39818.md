# [M] libheif has a NULL pointer dereference in heif_image_handle_get_image_tiling for malformed unci image missing ispe

## Summary
Severity: Medium
Advisory: CVE-2026-47709
Aliases: GHSA-4h72-vqgp-9376
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47709
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions prior to 1.22.0 crashes in the public C API `heif_image_handle_get_image_tiling()` when a malformed uncompressed HEIF image item has an associated `uncC` property but no associated `ispe` property. In debug builds this trips the `ispe && uncC` assertion in `ImageItem_uncompressed::get_heif_image_tiling()`. In a release/NDEBUG ASan build, the same file causes a null pointer read at address `0xa8`. Version 1.22.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47709.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-4h72-vqgp-9376
- https://nvd.nist.gov/vuln/detail/CVE-2026-47709
- https://github.com/strukturag/libheif/issues/1802
- https://github.com/strukturag/libheif/pull/1806
