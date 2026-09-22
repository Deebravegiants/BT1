# [M] CVE-2016-4037

## Summary
Severity: Medium
Advisory: CVE-2016-4037
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4037
Type: osv

## Details
The ehci_advance_state function in hw/usb/hcd-ehci.c in QEMU allows local guest OS administrators to cause a denial of service (infinite loop and CPU consumption) via a circular split isochronous transfer descriptor (siTD) list, a related issue to CVE-2015-8558.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=1ae3f2f178087711f9591350abad133525ba93f2
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183275.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183350.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184209.html
- http://www.securityfocus.com/bid/86283
- http://www.ubuntu.com/usn/USN-2974-1
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-04/msg02734.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-04/msg02691.html
- http://www.openwall.com/lists/oss-security/2016/04/18/3
- http://www.openwall.com/lists/oss-security/2016/04/18/6
