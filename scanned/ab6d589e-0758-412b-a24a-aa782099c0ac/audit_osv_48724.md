# [H] CVE-2018-12233

## Summary
Severity: High
Advisory: CVE-2018-12233
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-12233
Type: osv

## Details
In the ea_get function in fs/jfs/xattr.c in the Linux kernel through 4.17.1, a memory corruption bug in JFS can be triggered by calling setxattr twice with two different extended attribute names on the same file. This vulnerability can be triggered by an unprivileged user with the ability to create files and execute programs. A kmalloc call is incorrect, leading to slab-out-of-bounds in jfs_xattr.

## References
- http://www.securityfocus.com/bid/104452
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3752-3/
- https://usn.ubuntu.com/3754-1/
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://lkml.org/lkml/2018/6/2/2
- https://marc.info/?l=linux-kernel&m=152814391530549&w=2
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3753-1/
- https://usn.ubuntu.com/3753-2/
