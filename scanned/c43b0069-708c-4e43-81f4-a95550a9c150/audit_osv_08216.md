# [H] CVE-2016-1522

## Summary
Severity: High
Advisory: CVE-2016-1522
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/CVE-2016-1522
Type: osv

## Details
Code.cpp in Libgraphite in Graphite 2 1.2.4, as used in Mozilla Firefox before 43.0 and Firefox ESR 38.x before 38.6.1, does not consider recursive load calls during a size check, which allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly execute arbitrary code via a crafted Graphite smart font.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00058.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/82991
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177520.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184623.html
- http://rhn.redhat.com/errata/RHSA-2016-0197.html
- http://rhn.redhat.com/errata/RHSA-2016-0258.html
- http://rhn.redhat.com/errata/RHSA-2016-0594.html
- http://www.debian.org/security/2016/dsa-3479
- http://www.mozilla.org/security/announce/2016/mfsa2016-14.html
- http://www.ubuntu.com/usn/USN-2902-1
- https://security.gentoo.org/glsa/201701-35
- https://security.gentoo.org/glsa/201701-63
- http://blog.talosintel.com/2016/02/vulnerability-spotlight-libgraphite.html
