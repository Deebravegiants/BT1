# [H] nilfs2: fix potential out-of-bounds memory access in nilfs_find_entry()

## Summary
Severity: High
Advisory: CVE-2024-56619
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56619
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix potential out-of-bounds memory access in nilfs_find_entry()

Syzbot reported that when searching for records in a directory where the
inode's i_size is corrupted and has a large value, memory access outside
the folio/page range may occur, or a use-after-free bug may be detected if
KASAN is enabled.

This is because nilfs_last_byte(), which is called by nilfs_find_entry()
and others to calculate the number of valid bytes of directory data in a
page from i_size and the page index, loses the upper 32 bits of the 64-bit
size information due to an inappropriate type of local variable to which
the i_size value is assigned.

This caused a large byte offset value due to underflow in the end address
calculation in the calling nilfs_find_entry(), resulting in memory access
that exceeds the folio/page size.

Fix this issue by changing the type of the local variable causing the bit
loss from "unsigned int" to "u64".  The return value of nilfs_last_byte()
is also of type "unsigned int", but it is truncated so as not to exceed
PAGE_SIZE and no bit loss occurs, so no change is required.

## References
- https://git.kernel.org/stable/c/09d6d05579fd46e61abf6e457bb100ff11f3a9d3
- https://git.kernel.org/stable/c/31f7b57a77d4c82a34ddcb6ff35b5aa577ef153e
- https://git.kernel.org/stable/c/48eb6e7404948032bbe811c5affbe39f6b316951
- https://git.kernel.org/stable/c/5af8366625182f01f6d8465c9a3210574673af57
- https://git.kernel.org/stable/c/985ebec4ab0a28bb5910c3b1481a40fbf7f9e61d
- https://git.kernel.org/stable/c/c3afea07477baccdbdec4483f8d5e59d42a3f67f
- https://git.kernel.org/stable/c/e3732102a9d638d8627d14fdf7b208462f0520e0
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56619.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56619
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
