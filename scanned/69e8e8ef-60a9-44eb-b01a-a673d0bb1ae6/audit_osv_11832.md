# [H] CVE-2017-9992

## Summary
Severity: High
Advisory: CVE-2017-9992
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9992
Type: osv

## Details
Heap-based buffer overflow in the decode_dds1 function in libavcodec/dfa.c in FFmpeg before 2.8.12, 3.0.x before 3.0.8, 3.1.x before 3.1.8, 3.2.x before 3.2.5, and 3.3.x before 3.3.1 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-4012
- http://www.securityfocus.com/bid/99319
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1345
- https://github.com/FFmpeg/FFmpeg/commit/f52fbf4f3ed02a7d872d8a102006f29b4421f360
