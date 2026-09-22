# [M] CVE-2016-9830

## Summary
Severity: Medium
Advisory: CVE-2016-9830
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2016-9830
Type: osv

## Details
The MagickRealloc function in memory.c in Graphicsmagick 1.3.25 allows remote attackers to cause a denial of service (crash) via large dimensions in a jpeg image.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00141.html
- http://www.debian.org/security/2016/dsa-3746
- http://www.openwall.com/lists/oss-security/2016/12/05/5
- http://www.securityfocus.com/bid/94625
- https://blogs.gentoo.org/ago/2016/12/01/graphicsmagick-memory-allocation-failure-in-magickrealloc-memory-c
- https://bugzilla.redhat.com/show_bug.cgi?id=1401536
- http://hg.code.sf.net/p/graphicsmagick/code/rev/38d0f281e8c8
