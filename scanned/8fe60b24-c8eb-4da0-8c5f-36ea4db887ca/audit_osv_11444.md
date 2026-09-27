# [C] CVE-2017-7862

## Summary
Severity: Critical
Advisory: CVE-2017-7862
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7862
Type: osv

## Details
FFmpeg before 2017-02-07 has an out-of-bounds write caused by a heap-based buffer overflow related to the decode_frame function in libavcodec/pictordec.c.

## References
- http://www.debian.org/security/2017/dsa-4012
- http://www.securityfocus.com/bid/97676
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=559
- https://security.gentoo.org/glsa/201811-19
- https://github.com/FFmpeg/FFmpeg/commit/8c2ea3030af7b40a3c4275696fb5c76cdb80950a
