# [C] CVE-2016-4002

## Summary
Severity: Critical
Advisory: CVE-2016-4002
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-26
Source: https://osv.dev/vulnerability/CVE-2016-4002
Type: osv

## Details
Buffer overflow in the mipsnet_receive function in hw/net/mipsnet.c in QEMU, when the guest NIC is configured to accept large packets, allows remote attackers to cause a denial of service (memory corruption and QEMU crash) or possibly execute arbitrary code via a packet larger than 1514 bytes.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183275.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183350.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184209.html
- http://www.securityfocus.com/bid/85992
- http://www.ubuntu.com/usn/USN-2974-1
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- http://www.openwall.com/lists/oss-security/2016/04/11/6
- http://www.openwall.com/lists/oss-security/2016/04/12/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1326082
- https://lists.gnu.org/archive/html/qemu-devel/2016-04/msg01131.html
