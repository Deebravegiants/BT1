# [M] JLSEC-2026-1099

## Summary
Severity: Medium
Advisory: JLSEC-2026-1099
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1099
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions prior to 1.22.0 crashes in the public C API `heif_image_handle_get_image_tiling()` when a malformed uncompressed HEIF image item has an associated `uncC` property but no associated `ispe` property. In debug builds this trips the `ispe && uncC` assertion in `ImageItem_uncompressed::get_heif_image_tiling()`. In a release/NDEBUG ASan build, the same file causes a null pointer read at address `0xa8`. Version 1.22.0 fixes the issue.

## References
- https://github.com/strukturag/libheif/issues/1802
- https://github.com/strukturag/libheif/pull/1806
- https://github.com/strukturag/libheif/security/advisories/GHSA-4h72-vqgp-9376
