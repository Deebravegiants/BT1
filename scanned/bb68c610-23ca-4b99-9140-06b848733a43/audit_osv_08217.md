# [M] CVE-2016-1523

## Summary
Severity: Medium
Advisory: CVE-2016-1523
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/CVE-2016-1523
Type: osv

## Details
The SillMap::readFace function in FeatureMap.cpp in Libgraphite in Graphite 2 1.2.4, as used in Mozilla Firefox before 43.0 and Firefox ESR 38.x before 38.6.1, mishandles a return value, which allows remote attackers to cause a denial of service (missing initialization, NULL pointer dereference, and application crash) via a crafted Graphite smart font.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00088.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/82991
- http://www.securitytracker.com/id/1035017
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177520.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184623.html
- http://rhn.redhat.com/errata/RHSA-2016-0197.html
- http://rhn.redhat.com/errata/RHSA-2016-0258.html
- http://rhn.redhat.com/errata/RHSA-2016-0594.html
- http://www.debian.org/security/2016/dsa-3477
- http://www.debian.org/security/2016/dsa-3479
- http://www.debian.org/security/2016/dsa-3491
- http://www.ubuntu.com/usn/USN-2902-1
- http://www.ubuntu.com/usn/USN-2904-1
- https://security.gentoo.org/glsa/201605-06
