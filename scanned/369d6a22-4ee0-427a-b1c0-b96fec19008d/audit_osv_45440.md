# [M] JLSEC-2026-1170

## Summary
Severity: Medium
Advisory: JLSEC-2026-1170
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1170
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=8.0.0+0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0

## Details
Out-of-bounds read in FFmpeg 8.0 and 8.0.1 RV60 video decoder (`libavcodec/rv60dec.c`). The quantization parameter (qp) validation at line 2267 only checks the lower bound (qp < 0) but is missing upper bound validation. The qp value can reach 65 (base value 63 from 6-bit frame header + offset +2 from `read_qp_offset`) while the `rv60_qp_to_idx` array has size 64 (valid indices 0-63). This results in out-of-bounds array access at lines 1554 (`decode_cbp8`), 1655 (`decode_cbp16`), and 1419/1421 (`get_c4x4_set`), potentially leading to memory disclosure or crash. A previous fix in commit 61cbcaf93f added validation only for intra frames. This vulnerability affects the released versions 8.0 (released 2025-08-22) and 8.0.1 (released 2025-11-20) and is fixed in git master commit 8abeb879df which will be included in FFmpeg 8.1.

## References
- https://github.com/FFmpeg/FFmpeg/commit/8abeb879df66ea8d27ce1735925ced5a30813de4
- https://github.com/FFmpeg/FFmpeg/releases/tag/n8.0
- https://github.com/FFmpeg/FFmpeg/releases/tag/n8.0.1
