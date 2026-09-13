# [H] configfs_lookup(): don't leave ->s_dentry dangling on failure

## Summary
Severity: High
Advisory: CVE-2026-74359
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74359
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

configfs_lookup(): don't leave ->s_dentry dangling on failure

Normally ->s_dentry is cleared when dentry it's pointing to becomes
negative (on eviction, realistically).  However, that only happens
if dentry gets to be positive in the first place; in case of inode
allocation failure dentry never becomes positive, so ->d_iput()
is not called at all.

We do part of what normally would've been done by configfs_d_iput()
(dropping the reference to configfs_dirent) manually, but we do
not clear ->s_dentry there.  Sloppy as it is, it does not matter in
case of configfs_create_{dir,link}() - there configfs_dirent does
not survive dropping the sole reference to it.

However, for configfs_lookup() it *does* survive, with a dangling
pointer to soon to be freed dentry sitting it its ->s_dentry.

Subsequent getdents(2) in that directory will end up dereferencing
that pointer in order to pick the inode number.  Use after free...

This is the minimal fix; the right approach is to set the linkage
between dentry and configfs_dirent only after we know that we have
an inode, but that takes more surgery and the bug had been there
since 2006, so...

## References
- https://git.kernel.org/stable/c/10da12d352b7b2bb330a8609fdda9a58bf0e9856
- https://git.kernel.org/stable/c/3e83b2203aa59bd279e4f677ec793d49dc9d019e
- https://git.kernel.org/stable/c/57088b06109f3222963c639d8d743f42c2899b13
- https://git.kernel.org/stable/c/9c747dcee164ead300de90550ad9e4122f0d1bbb
- https://git.kernel.org/stable/c/b6e9c82522ddaa3ac0706b295ff4a71975d4f883
- https://git.kernel.org/stable/c/c3b073a209a9baa691b744318ac929fecdd8847c
- https://git.kernel.org/stable/c/eee07d769da5ac4e4f7bd0bc17828646a318d499
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74359.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74359
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
