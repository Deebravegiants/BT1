# [M] CVE-2017-8112

## Summary
Severity: Medium
Advisory: CVE-2017-8112
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-05-02
Source: https://osv.dev/vulnerability/CVE-2017-8112
Type: osv

## Details
hw/scsi/vmw_pvscsi.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (infinite loop and CPU consumption) via the message ring page count.

## References
- http://www.openwall.com/lists/oss-security/2017/04/26/5
- http://www.securityfocus.com/bid/98015
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201706-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1445621
- https://lists.gnu.org/archive/html/qemu-devel/2017-04/msg04578.html
