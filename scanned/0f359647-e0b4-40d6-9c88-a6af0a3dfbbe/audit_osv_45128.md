# [H] FFmpeg <=4.3 contains a buffer overflow vulnerability in libavcodec through a crafted file that may...

## Summary
Severity: High
Advisory: JLSEC-2025-112
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-112
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <4.4.2+0

## Details
FFmpeg <=4.3 contains a buffer overflow vulnerability in libavcodec through a crafted file that may lead to remote code execution.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commitdiff%3Bh=d6f293353c94c7ce200f6e0975ae3de49787f91f
- https://security.gentoo.org/glsa/202105-24
- https://trac.ffmpeg.org/ticket/8845
- https://trac.ffmpeg.org/ticket/8863
