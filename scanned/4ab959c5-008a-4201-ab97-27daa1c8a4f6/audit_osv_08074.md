# [C] CVE-2016-10192

## Summary
Severity: Critical
Advisory: CVE-2016-10192
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2016-10192
Type: osv

## Details
Heap-based buffer overflow in ffserver.c in FFmpeg before 2.8.10, 3.0.x before 3.0.5, 3.1.x before 3.1.6, and 3.2.x before 3.2.2 allows remote attackers to execute arbitrary code by leveraging failure to check chunk size.

## References
- http://www.securityfocus.com/bid/95991
- https://ffmpeg.org/security.html
- http://www.openwall.com/lists/oss-security/2017/01/31/12
- http://www.openwall.com/lists/oss-security/2017/02/02/1
- https://github.com/FFmpeg/FFmpeg/commit/a5d25faa3f4b18dac737fdb35d0dd68eb0dc2156
