# [H] CVE-2014-9627

## Summary
Severity: High
Advisory: CVE-2014-9627
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/CVE-2014-9627
Type: osv

## Details
The MP4_ReadBox_String function in modules/demux/mp4/libmp4.c in VideoLAN VLC media player before 2.1.6 performs an incorrect cast operation from a 64-bit integer to a 32-bit integer, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via a large box size.

## References
- http://openwall.com/lists/oss-security/2015/01/20/5
- https://github.com/videolan/vlc/commit/2e7c7091a61aa5d07e7997b393d821e91f593c39
- https://www.videolan.org/security/sa1501.html
- http://openwall.com/lists/oss-security/2015/01/20/5
- http://openwall.com/lists/oss-security/2015/01/20/5
- https://github.com/videolan/vlc/commit/2e7c7091a61aa5d07e7997b393d821e91f593c39
