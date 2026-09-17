# [C] CVE-2017-7865

## Summary
Severity: Critical
Advisory: CVE-2017-7865
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7865
Type: osv

## Details
FFmpeg before 2017-01-24 has an out-of-bounds write caused by a heap-based buffer overflow related to the ipvideo_decode_block_opcode_0xA function in libavcodec/interplayvideo.c and the avcodec_align_dimensions2 function in libavcodec/utils.c.

## References
- http://www.securityfocus.com/bid/97685
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=452
- https://lists.debian.org/debian-lts-announce/2019/02/msg00005.html
- https://github.com/FFmpeg/FFmpeg/commit/2080bc33717955a0e4268e738acf8c1eeddbf8cb
