# [H] CVE-2017-9994

## Summary
Severity: High
Advisory: CVE-2017-9994
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9994
Type: osv

## Details
libavcodec/webp.c in FFmpeg before 2.8.12, 3.0.x before 3.0.8, 3.1.x before 3.1.8, 3.2.x before 3.2.5, and 3.3.x before 3.3.1 does not ensure that pix_fmt is set, which allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted file, related to the vp8_decode_mb_row_no_filter and pred8x8_128_dc_8_c functions.

## References
- http://www.securityfocus.com/bid/99317
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1434
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1435
- https://github.com/FFmpeg/FFmpeg/commit/6b5d3fb26fb4be48e4966e4b1d97c2165538d4ef
