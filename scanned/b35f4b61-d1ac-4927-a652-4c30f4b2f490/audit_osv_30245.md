# [M] nilfs2: fix potential deadlock with newly created symlinks

## Summary
Severity: Medium
Advisory: CVE-2024-50229
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50229
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix potential deadlock with newly created symlinks

Syzbot reported that page_symlink(), called by nilfs_symlink(), triggers
memory reclamation involving the filesystem layer, which can result in
circular lock dependencies among the reader/writer semaphore
nilfs->ns_segctor_sem, s_writers percpu_rwsem (intwrite) and the
fs_reclaim pseudo lock.

This is because after commit 21fc61c73c39 ("don't put symlink bodies in
pagecache into highmem"), the gfp flags of the page cache for symbolic
links are overwritten to GFP_KERNEL via inode_nohighmem().

This is not a problem for symlinks read from the backing device, because
the __GFP_FS flag is dropped after inode_nohighmem() is called.  However,
when a new symlink is created with nilfs_symlink(), the gfp flags remain
overwritten to GFP_KERNEL.  Then, memory allocation called from
page_symlink() etc.  triggers memory reclamation including the FS layer,
which may call nilfs_evict_inode() or nilfs_dirty_inode().  And these can
cause a deadlock if they are called while nilfs->ns_segctor_sem is held:

Fix this issue by dropping the __GFP_FS flag from the page cache GFP flags
of newly created symlinks in the same way that nilfs_new_inode() and
__nilfs_read_inode() do, as a workaround until we adopt nofs allocation
scope consistently or improve the locking constraints.

## References
- https://git.kernel.org/stable/c/1246d86e7bbde265761932c6e2dce28c69cdcb91
- https://git.kernel.org/stable/c/58c7f44c7b9e5ac7e3b1e5da2572ed7767a12f38
- https://git.kernel.org/stable/c/69548bb663fcb63f9ee0301be808a36b9d78dac3
- https://git.kernel.org/stable/c/9aa5d43ac4cace8fb9bd964ff6c23f599dc3cd24
- https://git.kernel.org/stable/c/a1686db1e59f8fc016c4c9361e2119dd206f479a
- https://git.kernel.org/stable/c/b3a033e3ecd3471248d474ef263aadc0059e516a
- https://git.kernel.org/stable/c/c72e0df0b56c1166736dc8eb62070ebb12591447
- https://git.kernel.org/stable/c/cc38c596e648575ce58bfc31623a6506eda4b94a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50229.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50229
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
