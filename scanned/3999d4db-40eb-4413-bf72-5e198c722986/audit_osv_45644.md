# [M] JLSEC-2026-159

## Summary
Severity: Medium
Advisory: JLSEC-2026-159
Ecosystem: Julia
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/JLSEC-2026-159
Type: osv

## Affected
- Julia: `libde265_jll` — affected >=0 <1.0.18000+0

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.17, a crafted HEVC bitstream causes an out-of-bounds heap write confirmed by AddressSanitizer. The trigger is a stale `ctb_info.log2unitSize` after an SPS change where PicWidthInCtbsY and PicHeightInCtbsY stay constant but Log2CtbSizeY changes, causing `set_SliceHeaderIndex` to index past the allocated image metadata array and write 2 bytes past the end of a heap allocation. This issue has been patched in version 1.0.17.

## References
- https://github.com/strukturag/libde265/commit/c7891e412106130b83f8e8ea8b7f907e9449b658
- https://github.com/strukturag/libde265/releases/tag/v1.0.17
- https://github.com/strukturag/libde265/security/advisories/GHSA-653q-9f73-8hvg
