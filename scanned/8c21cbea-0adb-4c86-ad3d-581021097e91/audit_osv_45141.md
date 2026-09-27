# [H] An issue was discovered in `decode_frame` in `libavcodec/tiff.c` in FFmpeg version 4.3, allows...

## Summary
Severity: High
Advisory: JLSEC-2025-124
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-124
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.3.1+0 <4.3.1+2

## Details
An issue was discovered in `decode_frame` in `libavcodec/tiff.c` in FFmpeg version 4.3, allows remote attackers to cause a denial of service (DoS).

## References
- https://github.com/FFmpeg/FFmpeg/commit/292e41ce650a7b5ca5de4ae87fff0d6a90d9fc97
- https://lists.ffmpeg.org/pipermail/ffmpeg-devel/2020-November/272001.html
- https://trac.ffmpeg.org/ticket/8960
