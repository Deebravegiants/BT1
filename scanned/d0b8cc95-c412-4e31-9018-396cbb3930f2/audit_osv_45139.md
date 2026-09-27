# [M] A null pointer dereference issue was discovered in 'FFmpeg' in `decode_main_header()` function of...

## Summary
Severity: Medium
Advisory: JLSEC-2025-122
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-122
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A null pointer dereference issue was discovered in 'FFmpeg' in `decode_main_header()` function of `libavformat/nutdec.c` file. The flaw occurs because the function lacks check of the return value of `avformat_new_stream()` and triggers the null pointer dereference error, causing an application to crash.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2157054
- https://github.com/FFmpeg/FFmpeg/commit/9cf652cef49d74afe3d454f27d49eb1a1394951e
- https://lists.debian.org/debian-lts-announce/2023/06/msg00016.html
