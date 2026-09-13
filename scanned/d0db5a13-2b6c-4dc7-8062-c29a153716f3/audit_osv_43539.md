# [H] kernfs: fix xattr race condition with multiple superblocks

## Summary
Severity: High
Advisory: CVE-2026-74343
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74343
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

kernfs: fix xattr race condition with multiple superblocks

Multiple superblocks with different namespaces can share the same
kernfs_node when kernfs_test_super() finds a matching root but
different namespace. This means multiple inodes from different
superblocks can reference the same kernfs_node->iattr->xattrs
structure.

The VFS layer only holds per-inode locks during xattr operations,
which is insufficient to serialize concurrent xattr modifications on
the shared kernfs_node. This can lead to race conditions in
simple_xattr_set() where the lookup->replace/remove sequence is not
atomic with respect to operations from other superblocks.

Fix this by protecting xattr operations with the existing hashed
kernfs_locks->open_file_mutex[] array, which is already used to
protect per-node open file data. The hashed mutex array provides
scalable per-node serialization (scaled by CPU count, up to 1024 locks
on 32+ CPU systems) with zero memory overhead.

Changes:
- Rename open_file_mutex[] to node_mutex[] to reflect dual purpose
- Add kernfs_node_lock_ptr() and kernfs_node_lock() helpers
- Protect simple_xattr_set() calls in kernfs_xattr_set() and
  kernfs_vfs_user_xattr_set() with the hashed mutex
- Update file.c to use new helpers via compatibility wrappers
- Update documentation to explain the extended lock usage

## References
- https://git.kernel.org/stable/c/6a07814ff643b5c8e1353d8c6229f52fde205cde
- https://git.kernel.org/stable/c/bf53db51359939755084d08156684ed649489592
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74343.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74343
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
