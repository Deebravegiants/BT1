# [C] In FFmpeg before 4.2, `avcodec_open2` in `libavcodec/utils.c` allows a NULL pointer dereference and...

## Summary
Severity: Critical
Advisory: JLSEC-2025-106
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-106
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <4.3.1+0

## Details
In FFmpeg before 4.2, `avcodec_open2` in `libavcodec/utils.c` allows a NULL pointer dereference and possibly unspecified other impact when there is no valid close function pointer.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15733
- https://github.com/FFmpeg/FFmpeg/commit/8df6884832ec413cf032dfaa45c23b1c7876670c
- https://lists.debian.org/debian-lts-announce/2021/01/msg00026.html
- https://security.gentoo.org/glsa/202003-65
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2020/dsa-4722
