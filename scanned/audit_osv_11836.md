# [H] CVE-2017-9996

## Summary
Severity: High
Advisory: CVE-2017-9996
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9996
Type: osv

## Details
The cdxl_decode_frame function in libavcodec/cdxl.c in FFmpeg 2.8.x before 2.8.12, 3.0.x before 3.0.8, 3.1.x before 3.1.8, 3.2.x before 3.2.5, and 3.3.x before 3.3.1 does not exclude the CHUNKY format, which allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted file.

## References
- http://www.securityfocus.com/bid/99323
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1378
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1427
- https://github.com/FFmpeg/FFmpeg/commit/1e42736b95065c69a7481d0cf55247024f54b660
- https://github.com/FFmpeg/FFmpeg/commit/e1b60aad77c27ed5d4dfc11e5e6a05a38c70489d
