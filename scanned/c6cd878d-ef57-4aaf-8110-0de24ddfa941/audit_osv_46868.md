# [C] CVE-2015-7512

## Summary
Severity: Critical
Advisory: CVE-2015-7512
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2015-7512
Type: osv

## Details
Buffer overflow in the pcnet_receive function in hw/net/pcnet.c in QEMU, when a guest NIC has a larger MTU, allows remote attackers to cause a denial of service (guest OS crash) or execute arbitrary code via a large packet.

## References
- http://rhn.redhat.com/errata/RHSA-2015-2694.html
- http://rhn.redhat.com/errata/RHSA-2015-2695.html
- http://rhn.redhat.com/errata/RHSA-2015-2696.html
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/11/30/3
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/78230
- http://www.securitytracker.com/id/1034527
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2015/11/30/3
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=8b98a2f07175d46c3f7217639bd5e03f
