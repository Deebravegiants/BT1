# [M] CVE-2018-18690

## Summary
Severity: Medium
Advisory: CVE-2018-18690
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-26
Source: https://osv.dev/vulnerability/CVE-2018-18690
Type: osv

## Details
In the Linux kernel before 4.17, a local attacker able to set attributes on an xfs filesystem could make this filesystem non-operational until the next mount by triggering an unchecked error condition during an xfs attribute change, because xfs_attr_shortform_addname in fs/xfs/libxfs/xfs_attr.c mishandles ATTR_REPLACE operations with conversion of an attr from short to long form.

## References
- https://usn.ubuntu.com/3847-1/
- https://usn.ubuntu.com/3847-2/
- https://usn.ubuntu.com/3847-3/
- https://usn.ubuntu.com/3848-1/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3849-2/
- http://www.securityfocus.com/bid/105753
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://usn.ubuntu.com/3848-2/
- https://usn.ubuntu.com/3849-1/
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://bugzilla.suse.com/show_bug.cgi?id=1105025
- https://bugzilla.kernel.org/show_bug.cgi?id=199119
- https://github.com/torvalds/linux/commit/7b38460dc8e4eafba06c78f8e37099d3b34d473c
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7b38460dc8e4eafba06c78f8e37099d3b34d473c
