# [C] FFmpeg n6.1.1 has an Out-of-bounds Read via `libavcodec/ppc/vp8dsp_altivec.c`, static const `vec_s8`...

## Summary
Severity: Critical
Advisory: JLSEC-2025-141
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-141
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <6.1.2+0

## Details
FFmpeg n6.1.1 has an Out-of-bounds Read via `libavcodec/ppc/vp8dsp_altivec.c`, static const `vec_s8` `h_subpel_filters_outer`

## References
- https://gist.github.com/1047524396/9754a44845578358f6a403447c458ca4
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavcodec/ppc/vp8dsp_altivec.c#L53
- https://github.com/ffmpeg/ffmpeg/commit/09e6840cf7a3ee07a73c3ae88a020bf27ca1a667
- https://lists.debian.org/debian-lts-announce/2025/02/msg00000.html
