# [M] CVE-2018-10840

## Summary
Severity: Medium
Advisory: CVE-2018-10840
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/CVE-2018-10840
Type: osv

## Details
Linux kernel is vulnerable to a heap-based buffer overflow in the fs/ext4/xattr.c:ext4_xattr_set_entry() function. An attacker could exploit this by operating on a mounted crafted ext4 image.

## References
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- http://www.securityfocus.com/bid/104858
- https://access.redhat.com/errata/RHSA-2019:0162
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10840
