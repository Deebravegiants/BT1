# [H] LIBPNG has an out-of-bounds read in png_image_read_composite

## Summary
Severity: High
Advisory: CVE-2025-66293
Aliases: GHSA-9mpm-9pxh-mg4f
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2025-66293
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. Prior to 1.6.52, an out-of-bounds read vulnerability in libpng's simplified API allows reading up to 1012 bytes beyond the png_sRGB_base[512] array when processing valid palette PNG images with partial transparency and gamma correction. The PNG files that trigger this vulnerability are valid per the PNG specification; the bug is in libpng's internal state management. Upgrade to libpng 1.6.52 or later.

## References
- http://www.openwall.com/lists/oss-security/2025/12/03/6
- http://www.openwall.com/lists/oss-security/2025/12/03/7
- http://www.openwall.com/lists/oss-security/2025/12/03/8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66293.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-9mpm-9pxh-mg4f
- https://nvd.nist.gov/vuln/detail/CVE-2025-66293
- https://github.com/pnggroup/libpng/issues/764
- https://github.com/pnggroup/libpng/commit/788a624d7387a758ffd5c7ab010f1870dea753a1
- https://github.com/pnggroup/libpng/commit/a05a48b756de63e3234ea6b3b938b8f5f862484a
