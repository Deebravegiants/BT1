# [M] heap out-of-bounds write in libde265 1.0.16

## Summary
Severity: Medium
Advisory: CVE-2026-33165
Aliases: GHSA-653q-9f73-8hvg
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33165
Type: osv

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.17, a crafted HEVC bitstream causes an out-of-bounds heap write confirmed by AddressSanitizer. The trigger is a stale ctb_info.log2unitSize after an SPS change where PicWidthInCtbsY and PicHeightInCtbsY stay constant but Log2CtbSizeY changes, causing set_SliceHeaderIndex to index past the allocated image metadata array and write 2 bytes past the end of a heap allocation. This issue has been patched in version 1.0.17.

## References
- https://github.com/strukturag/libde265/releases/tag/v1.0.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33165.json
- https://github.com/strukturag/libde265/security/advisories/GHSA-653q-9f73-8hvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33165
- https://github.com/strukturag/libde265/commit/c7891e412106130b83f8e8ea8b7f907e9449b658
