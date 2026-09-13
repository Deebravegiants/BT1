# [M] CVE-2016-3941

## Summary
Severity: Medium
Advisory: CVE-2016-3941
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-18
Source: https://osv.dev/vulnerability/CVE-2016-3941
Type: osv

## Details
Buffer overflow in the AStreamPeekStream function in input/stream.c in VideoLAN VLC media player before 2.2.0 allows remote attackers to cause a denial of service (crash) via a crafted wav file, related to "seek across EOF."

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00045.html
- http://www.securitytracker.com/id/1035456
- https://bugs.launchpad.net/ubuntu/+source/vlc/+bug/1533633
- https://mailman.videolan.org/pipermail/vlc-commits/2015-January/028938.html
