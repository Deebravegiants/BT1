# [M] libvips: Possible integer overflow when reading multi-page TIFF images via ImageMagick

## Summary
Severity: Medium
Advisory: CVE-2026-70651
Aliases: GHSA-7p29-wg2h-36q4
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-70651
Type: osv

## Details
libvips is a fast image processing library with low memory needs. Prior to version 8.18.3, libvips built without libtiff support but with ImageMagick support can overflow the combined frame height while loading a crafted multi-page TIFF through VipsForeignLoadMagick. The vulnerable calculations in libvips/foreign/magick6load.c and libvips/foreign/magick7load.c multiply the per-page Ysize by n_frames without a checked bound, which can cause a heap buffer over-read and process crash. Most package-manager builds include libtiff and do not use this affected fallback path. This issue is fixed in version 8.18.3.

## References
- https://github.com/libvips/libvips/releases/tag/v8.18.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70651.json
- https://github.com/libvips/libvips/security/advisories/GHSA-7p29-wg2h-36q4
- https://nvd.nist.gov/vuln/detail/CVE-2026-70651
- https://github.com/libvips/libvips/commit/05719ca3d5852acdeb6714de2e8e769c9a5d2c11
- https://github.com/libvips/libvips/pull/5040
