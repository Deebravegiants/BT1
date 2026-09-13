# [M] LIBPNG has an integer truncation causing heap buffer over-read in png_image_write_*

## Summary
Severity: Medium
Advisory: CVE-2026-22801
Aliases: GHSA-vgjq-8cw5-ggw8
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22801
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From 1.6.26 to 1.6.53, there is an integer truncation in the libpng simplified write API functions png_write_image_16bit and png_write_image_8bit causes heap buffer over-read when the caller provides a negative row stride (for bottom-up image layouts) or a stride exceeding 65535 bytes. The bug was introduced in libpng 1.6.26 (October 2016) by casts added to silence compiler warnings on 16-bit systems. This vulnerability is fixed in 1.6.54.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22801.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-vgjq-8cw5-ggw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-22801
