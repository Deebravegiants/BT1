# [C] CVE-2019-17542

## Summary
Severity: Critical
Advisory: CVE-2019-17542
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/CVE-2019-17542
Type: osv

## Details
FFmpeg before 4.2 has a heap-based buffer overflow in vqa_decode_chunk because of an out-of-array access in vqa_decode_init in libavcodec/vqavideo.c.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00003.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00022.html
- https://security.gentoo.org/glsa/202003-65
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2020/dsa-4722
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15919
- https://github.com/FFmpeg/FFmpeg/commit/02f909dc24b1f05cfbba75077c7707b905e63cd2
