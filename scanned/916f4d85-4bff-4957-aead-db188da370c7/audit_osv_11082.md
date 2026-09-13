# [M] CVE-2017-5973

## Summary
Severity: Medium
Advisory: CVE-2017-5973
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-5973
Type: osv

## Details
The xhci_kick_epctx function in hw/usb/hcd-xhci.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (infinite loop and QEMU process crash) via vectors related to control transfer descriptor sequence.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=f89b60f6e5fee3923bedf80e82b4e5efc1bb156b
- http://www.securityfocus.com/bid/96220
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201704-01
- http://www.openwall.com/lists/oss-security/2017/02/13/11
- https://bugzilla.redhat.com/show_bug.cgi?id=1421626
- https://lists.gnu.org/archive/html/qemu-devel/2017-02/msg01101.html
