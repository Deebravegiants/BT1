# [M] CVE-2015-8558

## Summary
Severity: Medium
Advisory: CVE-2015-8558
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2015-8558
Type: osv

## Details
The ehci_process_itd function in hw/usb/hcd-ehci.c in QEMU allows local guest OS administrators to cause a denial of service (infinite loop and CPU consumption) via a circular isochronous transfer descriptor (iTD) list.

## References
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/12/14/16
- http://www.openwall.com/lists/oss-security/2015/12/14/9
- http://www.securityfocus.com/bid/80694
- https://bugzilla.redhat.com/show_bug.cgi?id=1277983
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg02124.html
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2015/12/14/16
- http://www.openwall.com/lists/oss-security/2015/12/14/9
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg02124.html
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg02124.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1277983
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=156a2e4dbffa85997636a7a39ef12da6f1b40254
