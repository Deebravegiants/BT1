# [M] CVE-2019-19319

## Summary
Severity: Medium
Advisory: CVE-2019-19319
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2019-19319
Type: osv

## Details
In the Linux kernel before 5.2, a setxattr operation, after a mount of a crafted ext4 image, can cause a slab-out-of-bounds write access because of an ext4_xattr_set_entry use-after-free in fs/ext4/xattr.c when a large old_size value is used in a memset call, aka CID-345c0dbf3a30.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://usn.ubuntu.com/4391-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=345c0dbf3a30
- https://www.debian.org/security/2020/dsa-4698
- https://security.netapp.com/advisory/ntap-20200103-0001/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://bugzilla.suse.com/show_bug.cgi?id=1158021
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19319
