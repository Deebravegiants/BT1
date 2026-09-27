# [M] libheif: Integer underflow in Fraction constructor via double clap transform application

## Summary
Severity: Medium
Advisory: CVE-2026-62289
Aliases: GHSA-jc8f-p23p-5hjg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-62289
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In 1.23.0 and earlier, a crafted HEIF or AVIF file containing a clean aperture box can reduce an image dimension to zero and crash or corrupt tiling results when heif_image_handle_get_image_tiling(handle, 1, &tiling) is called. ImageItem::get_heif_image_tiling() returns already transformed dimensions, and process_image_transformations_on_tiling() applies the clean aperture transformation again. The second application passes zero to Box_clap::left_rounded(0), where image_width minus one underflows and constructs Fraction(0xFFFFFFFF, 2). Debug builds reach an assertion and abort, while release builds can return a corrupt crop and zero-width tiling result. The affected implementation spans libheif/image-items/image_item.cc, libheif/context.cc, and libheif/box.cc. This issue is fixed in version 1.23.1.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62289.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-jc8f-p23p-5hjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-62289
- https://github.com/strukturag/libheif/commit/f01870c1d7323a3003796d58eba7fff502be994c
