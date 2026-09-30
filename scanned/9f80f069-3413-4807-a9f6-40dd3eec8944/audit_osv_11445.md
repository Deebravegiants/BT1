# [C] CVE-2017-7863

## Summary
Severity: Critical
Advisory: CVE-2017-7863
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7863
Type: osv

## Details
FFmpeg before 2017-02-04 has an out-of-bounds write caused by a heap-based buffer overflow related to the decode_frame_common function in libavcodec/pngdec.c.

## References
- http://www.securityfocus.com/bid/97675
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=546
- https://lists.debian.org/debian-lts-announce/2019/02/msg00005.html
- https://github.com/FFmpeg/FFmpeg/commit/e477f09d0b3619f3d29173b2cd593e17e2d1978e
