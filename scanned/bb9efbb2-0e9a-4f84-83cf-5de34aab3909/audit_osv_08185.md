# [M] CVE-2016-1285

## Summary
Severity: Medium
Advisory: CVE-2016-1285
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-03-09
Source: https://osv.dev/vulnerability/CVE-2016-1285
Type: osv

## Details
named in ISC BIND 9.x before 9.9.8-P4 and 9.10.x before 9.10.3-P4 does not properly handle DNAME records when parsing fetch reply messages, which allows remote attackers to cause a denial of service (assertion failure and daemon exit) via a malformed packet to the rndc (aka control channel) interface, related to alist.c and sexpr.c.

## References
- https://kb.isc.org/article/AA-01438
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00013.html
- http://rhn.redhat.com/errata/RHSA-2016-0562.html
- http://rhn.redhat.com/errata/RHSA-2016-0601.html
- http://www.debian.org/security/2016/dsa-3511
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securitytracker.com/id/1035236
- http://www.ubuntu.com/usn/USN-2925-1
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05087821
- https://kb.isc.org/article/AA-01352
- https://kb.isc.org/article/AA-01380
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:13.bind.asc
- https://security.gentoo.org/glsa/201610-07
- http://marc.info/?l=bugtraq&m=146191105921542&w=2
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181036.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181037.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178831.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178880.html
