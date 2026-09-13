# [C] FFmpeg before 4.2 has a heap-based buffer overflow in `vqa_decode_chunk` because of an out-of-array...

## Summary
Severity: Critical
Advisory: JLSEC-2025-107
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-107
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <4.3.1+0

## Details
FFmpeg before 4.2 has a heap-based buffer overflow in `vqa_decode_chunk` because of an out-of-array access in `vqa_decode_init` in `libavcodec/vqavideo.c`.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15919
- https://github.com/FFmpeg/FFmpeg/commit/02f909dc24b1f05cfbba75077c7707b905e63cd2
- https://lists.debian.org/debian-lts-announce/2019/12/msg00003.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00022.html
- https://security.gentoo.org/glsa/202003-65
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2020/dsa-4722
