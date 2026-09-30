# [M] libheif: Out-of-bounds read in uncompressed unci tile range slicing

## Summary
Severity: Medium
Advisory: CVE-2026-62292
Aliases: GHSA-73p7-m7gg-w2jv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-62292
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. From 1.19.0 until 1.23.1, a crafted uncompressed HEIF image using generic zlib unci full-item compression can crash an application that decodes an advertised tile with heif_image_handle_decode_image_tile(). In libheif/codecs/uncompressed/unc_decoder.cc, unc_decoder::fetch_tile_data() computes a large tile offset and unc_decoder::get_compressed_image_data_uncompressed() validates it with range_start_offset plus range_size. For the last advertised tile (4095, 4095), the addition can wrap to zero, bypass the bounds check, and pass an invalid source pointer and a one-terabyte length to memcpy. The observed result is an out-of-bounds read and process crash; opening the file alone does not trigger the issue because tile decoding is required. This issue is fixed in version 1.23.1.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62292.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-73p7-m7gg-w2jv
- https://nvd.nist.gov/vuln/detail/CVE-2026-62292
- https://github.com/strukturag/libheif/commit/089a809bf6bed1abae102d5e97b6bb8c4f53b515
