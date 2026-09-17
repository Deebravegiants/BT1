# [H] CVE-2014-9629

## Summary
Severity: High
Advisory: CVE-2014-9629
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/CVE-2014-9629
Type: osv

## Details
Integer overflow in the Encode function in modules/codec/schroedinger.c in VideoLAN VLC media player before 2.1.6 and 2.2.x before 2.2.1 allows remote attackers to conduct buffer overflow attacks and execute arbitrary code via a crafted length value.

## References
- http://openwall.com/lists/oss-security/2015/01/20/5
- https://github.com/videolan/vlc/commit/9bb0353a5c63a7f8c6fc853faa3df4b4df1f5eb5
- https://www.videolan.org/security/sa1501.html
- http://openwall.com/lists/oss-security/2015/01/20/5
- https://github.com/videolan/vlc/commit/9bb0353a5c63a7f8c6fc853faa3df4b4df1f5eb5
