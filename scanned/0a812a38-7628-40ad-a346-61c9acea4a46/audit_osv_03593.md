# [M] ALPINE-CVE-2026-33165

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33165
Ecosystem: Alpine:v3.24
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33165
Type: osv

## Affected
- Alpine:v3.24: `libde265` — affected >=0 <1.0.18-r0

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.17, a crafted HEVC bitstream causes an out-of-bounds heap write confirmed by AddressSanitizer. The trigger is a stale ctb_info.log2unitSize after an SPS change where PicWidthInCtbsY and PicHeightInCtbsY stay constant but Log2CtbSizeY changes, causing set_SliceHeaderIndex to index past the allocated image metadata array and write 2 bytes past the end of a heap allocation. This issue has been patched in version 1.0.17.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33165
