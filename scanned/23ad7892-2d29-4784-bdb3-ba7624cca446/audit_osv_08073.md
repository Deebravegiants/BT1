# [C] CVE-2016-10191

## Summary
Severity: Critical
Advisory: CVE-2016-10191
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2016-10191
Type: osv

## Details
Heap-based buffer overflow in libavformat/rtmppkt.c in FFmpeg before 2.8.10, 3.0.x before 3.0.5, 3.1.x before 3.1.6, and 3.2.x before 3.2.2 allows remote attackers to execute arbitrary code by leveraging failure to check for RTMP packet size mismatches.

## References
- http://www.securityfocus.com/bid/95989
- https://lists.debian.org/debian-lts-announce/2018/12/msg00009.html
- https://ffmpeg.org/security.html
- http://www.openwall.com/lists/oss-security/2017/01/31/12
- http://www.openwall.com/lists/oss-security/2017/02/02/1
- https://github.com/FFmpeg/FFmpeg/commit/7d57ca4d9a75562fa32e40766211de150f8b3ee7
