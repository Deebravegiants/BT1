# [M] CVE-2016-8576

## Summary
Severity: Medium
Advisory: CVE-2016-8576
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8576
Type: osv

## Details
The xhci_ring_fetch function in hw/usb/hcd-xhci.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) by leveraging failure to limit the number of link Transfer Request Blocks (TRB) to process.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=05f43d44e4bc26611ce25fd7d726e483f73363ce
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/10/6
- http://www.securityfocus.com/bid/93469
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201611-11
- http://www.openwall.com/lists/oss-security/2016/10/10/12
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg01265.html
