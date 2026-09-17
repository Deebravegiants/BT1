# [M] CVE-2018-14615

## Summary
Severity: Medium
Advisory: CVE-2018-14615
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2018-14615
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.10. There is a buffer overflow in truncate_inline_inode() in fs/f2fs/inline.c when umounting an f2fs image, because a length value may be negative.

## References
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- http://www.securityfocus.com/bid/104917
- https://bugzilla.kernel.org/show_bug.cgi?id=200421
