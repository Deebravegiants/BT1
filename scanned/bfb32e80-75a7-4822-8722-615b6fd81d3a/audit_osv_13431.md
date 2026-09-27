# [C] CVE-2018-19857

## Summary
Severity: Critical
Advisory: CVE-2018-19857
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/CVE-2018-19857
Type: osv

## Details
The CAF demuxer in modules/demux/caf.c in VideoLAN VLC media player 3.0.4 may read memory from an uninitialized pointer when processing magic cookies in CAF files, because a ReadKukiChunk() cast converts a return value to an unsigned int even if that value is negative. This could result in a denial of service and/or a potential infoleak.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00081.html
- https://git.videolan.org/?p=vlc.git%3Ba=commit%3Bh=0cc5ea748ee5ff7705dde61ab15dff8f58be39d0
- https://usn.ubuntu.com/4074-1/
- http://www.securityfocus.com/bid/106130
- https://www.debian.org/security/2019/dsa-4366
- https://dyntopia.com/advisories/013-vlc
