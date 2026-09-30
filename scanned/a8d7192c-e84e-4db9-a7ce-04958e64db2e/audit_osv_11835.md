# [H] CVE-2017-9995

## Summary
Severity: High
Advisory: CVE-2017-9995
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9995
Type: osv

## Details
libavcodec/scpr.c in FFmpeg 3.3 before 3.3.1 does not properly validate height and width data, which allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted file.

## References
- http://www.securityfocus.com/bid/99320
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1478
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1519
- https://github.com/FFmpeg/FFmpeg/commit/2171dfae8c065878a2e130390eb78cf2947a5b69
- https://github.com/FFmpeg/FFmpeg/commit/7ac5067146613997bb38442cb022d7f41321a706
