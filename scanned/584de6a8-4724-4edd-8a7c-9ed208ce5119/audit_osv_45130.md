# [H] `dwa_uncompress` in `libavcodec/exr.c` in FFmpeg 4.4 allows an out-of-bounds array access because...

## Summary
Severity: High
Advisory: JLSEC-2025-114
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-114
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <4.4.2+0

## Details
`dwa_uncompress` in `libavcodec/exr.c` in FFmpeg 4.4 allows an out-of-bounds array access because `dc_count` is not strictly checked.

## References
- https://github.com/FFmpeg/FFmpeg/commit/26d3c81bc5ef2f8c3f09d45eaeacfb4b1139a777
- https://security.gentoo.org/glsa/202312-14
