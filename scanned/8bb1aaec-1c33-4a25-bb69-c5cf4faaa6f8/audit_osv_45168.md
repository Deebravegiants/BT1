# [M] A vulnerability was found in FFmpeg up to 7.1

## Summary
Severity: Medium
Advisory: JLSEC-2025-150
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-150
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <7.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.1+0

## Details
A vulnerability was found in FFmpeg up to 7.1. It has been rated as problematic. Affected by this issue is the function `mov_read_trak` of the file `libavformat/mov.c` of the component MOV Parser. The manipulation leads to null pointer dereference. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used. The patch is identified as 43be8d07281caca2e88bfd8ee2333633e1fb1a13. It is recommended to apply a patch to fix this issue.

## References
- https://ffmpeg.org/
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/43be8d07281caca2e88bfd8ee2333633e1fb1a13
- https://trac.ffmpeg.org/attachment/ticket/11460/poc
- https://trac.ffmpeg.org/ticket/11460
- https://vuldb.com/?ctiid.295982
- https://vuldb.com/?id.295982
- https://vuldb.com/?submit.496930
