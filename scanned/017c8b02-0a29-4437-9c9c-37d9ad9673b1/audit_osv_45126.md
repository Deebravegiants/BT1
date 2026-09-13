# [M] `track_header` in `libavformat/vividas.c` in FFmpeg 4.3.1 has an out-of-bounds write because of...

## Summary
Severity: Medium
Advisory: JLSEC-2025-110
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-110
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.3.1+2 <4.4.0+0
- Julia: `FFplay_jll` — affected >=0 <4.4.4+0

## Details
`track_header` in `libavformat/vividas.c` in FFmpeg 4.3.1 has an out-of-bounds write because of incorrect extradata packing.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26622
- https://github.com/FFmpeg/FFmpeg/commit/27a99e2c7d450fef15594671eef4465c8a166bd7
- https://security.gentoo.org/glsa/202105-24
