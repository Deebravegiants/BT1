# [H] CVE-2018-7550

## Summary
Severity: High
Advisory: CVE-2018-7550
Aliases: GHSA-f49v-45qp-cv53
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2018-7550
Type: osv

## Details
The load_multiboot function in hw/i386/multiboot.c in Quick Emulator (aka QEMU) allows local guest OS users to execute arbitrary code on the QEMU host via a mh_load_end_addr value greater than mh_bss_end_addr, which triggers an out-of-bounds read or write memory access.

## References
- http://www.securityfocus.com/bid/103181
- https://access.redhat.com/errata/RHSA-2018:1369
- https://access.redhat.com/errata/RHSA-2018:2462
- https://github.com/orangecertcc/security-research/security/advisories/GHSA-f49v-45qp-cv53
- https://lists.debian.org/debian-lts-announce/2018/04/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/04/msg00016.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://usn.ubuntu.com/3649-1/
- https://www.debian.org/security/2018/dsa-4213
- https://bugzilla.redhat.com/show_bug.cgi?id=1549798
- https://lists.gnu.org/archive/html/qemu-devel/2018-02/msg06890.html
