# [H] An issue was discovered in the FFmpeg package, where `vp3_decode_frame` in `libavcodec/vp3.c` lacks...

## Summary
Severity: High
Advisory: JLSEC-2025-121
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-121
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
An issue was discovered in the FFmpeg package, where `vp3_decode_frame` in `libavcodec/vp3.c` lacks check of the return value of `av_malloc()` and will cause a null pointer dereference, impacting availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2153551
- https://github.com/FFmpeg/FFmpeg/commit/656cb0450aeb73b25d7d26980af342b37ac4c568
- https://lists.debian.org/debian-lts-announce/2023/06/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KOMB6WRUC55VWV25IKJTV22KARBUGWGQ/
- https://www.debian.org/security/2023/dsa-5394
