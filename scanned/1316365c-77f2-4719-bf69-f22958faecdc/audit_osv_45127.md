# [H] `decode_frame` in `libavcodec/exr.c` in FFmpeg 4.3.1 has an out-of-bounds write because of errors in...

## Summary
Severity: High
Advisory: JLSEC-2025-111
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-111
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.3.1+2 <4.4.0+0
- Julia: `FFplay_jll` — affected >=0 <4.4.4+0

## Details
`decode_frame` in `libavcodec/exr.c` in FFmpeg 4.3.1 has an out-of-bounds write because of errors in calculations of when to perform memset zero operations.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26532
- https://github.com/FFmpeg/FFmpeg/commit/3e5959b3457f7f1856d997261e6ac672bba49e8b
- https://github.com/FFmpeg/FFmpeg/commit/b0a8b40294ea212c1938348ff112ef1b9bf16bb3
- https://lists.debian.org/debian-lts-announce/2021/01/msg00026.html
- https://security.gentoo.org/glsa/202105-24
- https://www.debian.org/security/2021/dsa-4990
