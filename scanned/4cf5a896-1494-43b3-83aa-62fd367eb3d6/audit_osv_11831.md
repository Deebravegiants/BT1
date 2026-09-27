# [H] CVE-2017-9991

## Summary
Severity: High
Advisory: CVE-2017-9991
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9991
Type: osv

## Details
Heap-based buffer overflow in the xwd_decode_frame function in libavcodec/xwddec.c in FFmpeg before 2.8.12, 3.0.x before 3.0.8, 3.1.x before 3.1.8, 3.2.x before 3.2.5, and 3.3.x before 3.3.1 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted file.

## References
- http://www.securityfocus.com/bid/99316
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1399
- https://github.com/FFmpeg/FFmpeg/commit/441026fcb13ac23aa10edc312bdacb6445a0ad06
