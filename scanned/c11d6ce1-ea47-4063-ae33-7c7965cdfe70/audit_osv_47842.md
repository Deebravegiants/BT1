# [M] CVE-2017-13737

## Summary
Severity: Medium
Advisory: CVE-2017-13737
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13737
Type: osv

## Details
There is an invalid free in the MagickFree function in magick/memory.c in GraphicsMagick 1.3.26 that will lead to a remote denial of service attack.

## References
- https://usn.ubuntu.com/4222-1/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- http://www.securityfocus.com/bid/100518
- https://www.debian.org/security/2018/dsa-4321
- https://bugs.debian.org/878511
- https://bugzilla.redhat.com/show_bug.cgi?id=1484196
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/3db9449e3d6a/
- http://openwall.com/lists/oss-security/2017/08/29/4
