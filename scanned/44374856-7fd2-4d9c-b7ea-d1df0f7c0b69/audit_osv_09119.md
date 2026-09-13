# [M] CVE-2016-7995

## Summary
Severity: Medium
Advisory: CVE-2016-7995
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7995
Type: osv

## Details
Memory leak in the ehci_process_itd function in hw/usb/hcd-ehci.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (memory consumption) via a large number of crafted buffer page select (PG) indexes.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=b16c129daf0fed91febbb88de23dae8271c8898a
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/07/3
- http://www.openwall.com/lists/oss-security/2016/10/08/4
- http://www.securityfocus.com/bid/93454
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg06609.html
