# [H] Buffer Overflow vulnerability exists in FFmpeg 4.1 via `apng_do_inverse_blend` in...

## Summary
Severity: High
Advisory: JLSEC-2025-113
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-113
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <4.3.1+0

## Details
Buffer Overflow vulnerability exists in FFmpeg 4.1 via `apng_do_inverse_blend` in `libavcodec/pngenc.c`, which could let a remote malicious user cause a Denial of Service

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://trac.ffmpeg.org/ticket/7989
- https://www.debian.org/security/2021/dsa-4990
