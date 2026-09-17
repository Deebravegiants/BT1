# [C] CVE-2017-7866

## Summary
Severity: Critical
Advisory: CVE-2017-7866
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7866
Type: osv

## Details
FFmpeg before 2017-01-23 has an out-of-bounds write caused by a stack-based buffer overflow related to the decode_zbuf function in libavcodec/pngdec.c.

## References
- http://www.securityfocus.com/bid/97664
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=444
- https://github.com/FFmpeg/FFmpeg/commit/e371f031b942d73e02c090170975561fabd5c264
