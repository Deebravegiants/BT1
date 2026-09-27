# [H] CVE-2018-14678

## Summary
Severity: High
Advisory: CVE-2018-14678
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-28
Source: https://osv.dev/vulnerability/CVE-2018-14678
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.11, as used in Xen through 4.11.x. The xen_failsafe_callback entry point in arch/x86/entry/entry_64.S does not properly maintain RBX, which allows local users to cause a denial of service (uninitialized memory usage and system crash). Within Xen, 64-bit x86 PV Linux guest OS users can trigger a guest OS crash or possibly gain privileges.

## References
- https://usn.ubuntu.com/3931-1/
- https://usn.ubuntu.com/3931-2/
- https://www.debian.org/security/2018/dsa-4308
- http://www.securityfocus.com/bid/104924
- http://www.securitytracker.com/id/1041397
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://xenbits.xen.org/xsa/advisory-274.html
