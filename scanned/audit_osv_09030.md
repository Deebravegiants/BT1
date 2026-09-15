# [M] CVE-2016-7466

## Summary
Severity: Medium
Advisory: CVE-2016-7466
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7466
Type: osv

## Details
Memory leak in the usb_xhci_exit function in hw/usb/hcd-xhci.c in QEMU (aka Quick Emulator), when the xhci uses msix, allows local guest OS administrators to cause a denial of service (memory consumption and possibly QEMU process crash) by repeatedly unplugging a USB device.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=b53dd4495ced2432a0b652ea895e651d07336f7e
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/09/19/8
- http://www.openwall.com/lists/oss-security/2016/09/20/3
- http://www.securityfocus.com/bid/93029
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg02773.html
