# [M] CVE-2019-11474

## Summary
Severity: Medium
Advisory: CVE-2019-11474
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2019-11474
Type: osv

## Details
coders/xwd.c in GraphicsMagick 1.3.31 allows attackers to cause a denial of service (floating-point exception and application crash) by crafting an XWD image file, a different vulnerability than CVE-2019-11008 and CVE-2019-11009.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00055.html
- http://www.graphicsmagick.org/Changelog.html
- http://www.securityfocus.com/bid/108055
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00021.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00027.html
- https://usn.ubuntu.com/4207-1/
- https://www.debian.org/security/2020/dsa-4640
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/5402c5cbd8bd
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/944dcbc457f8
