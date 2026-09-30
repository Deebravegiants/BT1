# [H] CVE-2017-14167

## Summary
Severity: High
Advisory: CVE-2017-14167
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-09-08
Source: https://osv.dev/vulnerability/CVE-2017-14167
Type: osv

## Details
Integer overflow in the load_multiboot function in hw/i386/multiboot.c in QEMU (aka Quick Emulator) allows local guest OS users to execute arbitrary code on the host via crafted multiboot header address values, which trigger an out-of-bounds write.

## References
- http://www.debian.org/security/2017/dsa-3991
- http://www.securityfocus.com/bid/100694
- https://access.redhat.com/errata/RHSA-2017:3368
- https://access.redhat.com/errata/RHSA-2017:3369
- https://access.redhat.com/errata/RHSA-2017:3466
- https://access.redhat.com/errata/RHSA-2017:3470
- https://access.redhat.com/errata/RHSA-2017:3471
- https://access.redhat.com/errata/RHSA-2017:3472
- https://access.redhat.com/errata/RHSA-2017:3473
- https://access.redhat.com/errata/RHSA-2017:3474
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://usn.ubuntu.com/3575-1/
- http://www.openwall.com/lists/oss-security/2017/09/07/2
- https://lists.nongnu.org/archive/html/qemu-devel/2017-09/msg01032.html
