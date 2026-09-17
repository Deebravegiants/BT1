# [M] CVE-2017-9608

## Summary
Severity: Medium
Advisory: CVE-2017-9608
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-9608
Type: osv

## Details
The dnxhd decoder in FFmpeg before 3.2.6, and 3.3.x before 3.3.3 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted mov file.

## References
- http://www.openwall.com/lists/oss-security/2017/08/15/8
- http://www.securityfocus.com/bid/100348
- https://www.debian.org/security/2017/dsa-3957
- https://github.com/FFmpeg/FFmpeg/commit/0a709e2a10b8288a0cc383547924ecfe285cef89
- https://github.com/FFmpeg/FFmpeg/commit/31c1c0b46a7021802c3d1d18039fca30dba5a14e
- https://github.com/FFmpeg/FFmpeg/commit/611b35627488a8d0763e75c25ee0875c5b7987dd
- http://www.openwall.com/lists/oss-security/2017/08/14/1
