# [H] CVE-2017-9990

## Summary
Severity: High
Advisory: CVE-2017-9990
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9990
Type: osv

## Details
Stack-based buffer overflow in the color_string_to_rgba function in libavcodec/xpmdec.c in FFmpeg 3.3 before 3.3.1 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted file.

## References
- http://www.securityfocus.com/bid/99313
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1466
- https://github.com/FFmpeg/FFmpeg/commit/cb243972b121b1ae6b60a78ff55a0506c69f3879
