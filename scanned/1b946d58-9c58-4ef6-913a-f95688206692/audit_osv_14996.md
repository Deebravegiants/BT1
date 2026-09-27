# [C] CVE-2019-12874

## Summary
Severity: Critical
Advisory: CVE-2019-12874
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2019-12874
Type: osv

## Details
An issue was discovered in zlib_decompress_extra in modules/demux/mkv/util.cpp in VideoLAN VLC media player 3.x through 3.0.7. The Matroska demuxer, while parsing a malformed MKV file type, has a double free.

## References
- http://git.videolan.org/?p=vlc.git%3Ba=commit%3Bh=81023659c7de5ac2637b4a879195efef50846102
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00081.html
- http://www.securityfocus.com/bid/108882
- https://usn.ubuntu.com/4074-1/
- https://security.gentoo.org/glsa/201908-23
