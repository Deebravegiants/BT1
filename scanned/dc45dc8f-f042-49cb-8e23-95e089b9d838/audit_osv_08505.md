# [H] CVE-2016-4001

## Summary
Severity: High
Advisory: CVE-2016-4001
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4001
Type: osv

## Details
Buffer overflow in the stellaris_enet_receive function in hw/net/stellaris_enet.c in QEMU, when the Stellaris ethernet controller is configured to accept large packets, allows remote attackers to cause a denial of service (QEMU crash) via a large packet.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=3a15cc0e1ee7168db0782133d2607a6bfa422d66
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183275.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183350.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184209.html
- http://www.openwall.com/lists/oss-security/2016/04/11/4
- http://www.openwall.com/lists/oss-security/2016/04/12/6
- http://www.securityfocus.com/bid/85976
- http://www.ubuntu.com/usn/USN-2974-1
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-04/msg01334.html
