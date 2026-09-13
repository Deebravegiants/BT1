# [M] CVE-2019-19767

## Summary
Severity: Medium
Advisory: CVE-2019-19767
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-19767
Type: osv

## Details
The Linux kernel before 5.4.2 mishandles ext4_expand_extra_isize, as demonstrated by use-after-free errors in __ext4_expand_extra_isize and ext4_xattr_set_entry, related to fs/ext4/inode.c and fs/ext4/super.c, aka CID-4ea99936a163.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4284-1/
- https://usn.ubuntu.com/4287-1/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4258-1/
- https://usn.ubuntu.com/4287-2/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.2
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://bugzilla.kernel.org/show_bug.cgi?id=205609
- https://bugzilla.kernel.org/show_bug.cgi?id=205707
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4ea99936a1630f51fc3a2d61a58ec4a1c4b7d55a
- https://github.com/torvalds/linux/commit/4ea99936a1630f51fc3a2d61a58ec4a1c4b7d55a
