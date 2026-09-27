# [M] CVE-2017-6505

## Summary
Severity: Medium
Advisory: CVE-2017-6505
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6505
Type: osv

## Details
The ohci_service_ed_list function in hw/usb/hcd-ohci.c in QEMU (aka Quick Emulator) before 2.9.0 allows local guest OS users to cause a denial of service (infinite loop) via vectors involving the number of link endpoint list descriptors, a different vulnerability than CVE-2017-9330.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commitdiff%3Bh=95ed56939eb2eaa4e2f349fe6dcd13ca4edfd8fb
- http://www.securityfocus.com/bid/96611
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201704-01
- http://www.openwall.com/lists/oss-security/2017/03/06/6
- https://bugzilla.redhat.com/show_bug.cgi?id=1429432
