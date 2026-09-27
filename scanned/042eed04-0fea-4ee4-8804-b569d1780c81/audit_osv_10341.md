# [M] CVE-2017-15038

## Summary
Severity: Medium
Advisory: CVE-2017-15038
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-15038
Type: osv

## Details
Race condition in the v9fs_xattrwalk function in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local guest OS users to obtain sensitive information from host heap memory via vectors related to reading extended attributes.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://usn.ubuntu.com/3575-1/
- https://www.debian.org/security/2018/dsa-4213
- http://www.openwall.com/lists/oss-security/2017/10/06/1
- https://lists.gnu.org/archive/html/qemu-devel/2017-10/msg00729.html
