# [H] FFmpeg version (git commit de8e6e67e7523e48bb27ac224a0b446df05e1640) suffers from a an assertion...

## Summary
Severity: High
Advisory: JLSEC-2025-117
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-117
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.3.1+2 <4.4.0+0
- Julia: `FFplay_jll` — affected >=0 <4.4.4+0

## Details
FFmpeg version (git commit de8e6e67e7523e48bb27ac224a0b446df05e1640) suffers from a an assertion failure at `src/libavutil/mathematics.c`.

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00012.html
- https://security.gentoo.org/glsa/202312-14
- https://trac.ffmpeg.org/ticket/9312
- https://www.debian.org/security/2021/dsa-4990
- https://www.debian.org/security/2021/dsa-4998
