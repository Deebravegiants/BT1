# [M] JLSEC-2026-643

## Summary
Severity: Medium
Advisory: JLSEC-2026-643
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-643
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.0+0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=7.1.0+0 <8.1.2+0

## Details
FFmpeg git-master,N-113007-g8d24a28d06 was discovered to contain a segmentation violation via the component `/libavcodec/jpeg2000dec.c`.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00037.html
- https://trac.ffmpeg.org/ticket/11393
