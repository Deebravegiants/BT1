# [H] nilfs2: fix use-after-free of nilfs_root in dirtying inodes via iput

## Summary
Severity: High
Advisory: CVE-2023-53311
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53311
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.14.323, >=4.15.0 <4.19.292, >=4.20.0 <5.4.254, >=5.5.0 <5.10.191, >=5.11.0 <5.15.127, >=5.16.0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix use-after-free of nilfs_root in dirtying inodes via iput

During unmount process of nilfs2, nothing holds nilfs_root structure after
nilfs2 detaches its writer in nilfs_detach_log_writer().  Previously,
nilfs_evict_inode() could cause use-after-free read for nilfs_root if
inodes are left in "garbage_list" and released by nilfs_dispose_list at
the end of nilfs_detach_log_writer(), and this bug was fixed by commit
9b5a04ac3ad9 ("nilfs2: fix use-after-free bug of nilfs_root in
nilfs_evict_inode()").

However, it turned out that there is another possibility of UAF in the
call path where mark_inode_dirty_sync() is called from iput():

nilfs_detach_log_writer()
  nilfs_dispose_list()
    iput()
      mark_inode_dirty_sync()
        __mark_inode_dirty()
          nilfs_dirty_inode()
            __nilfs_mark_inode_dirty()
              nilfs_load_inode_block() --> causes UAF of nilfs_root struct

This can happen after commit 0ae45f63d4ef ("vfs: add support for a
lazytime mount option"), which changed iput() to call
mark_inode_dirty_sync() on its final reference if i_state has I_DIRTY_TIME
flag and i_nlink is non-zero.

This issue appears after commit 28a65b49eb53 ("nilfs2: do not write dirty
data after degenerating to read-only") when using the syzbot reproducer,
but the issue has potentially existed before.

Fix this issue by adding a "purging flag" to the nilfs structure, setting
that flag while disposing the "garbage_list" and checking it in
__nilfs_mark_inode_dirty().

Unlike commit 9b5a04ac3ad9 ("nilfs2: fix use-after-free bug of nilfs_root
in nilfs_evict_inode()"), this patch does not rely on ns_writer to
determine whether to skip operations, so as not to break recovery on
mount.  The nilfs_salvage_orphan_logs routine dirties the buffer of
salvaged data before attaching the log writer, so changing
__nilfs_mark_inode_dirty() to skip the operation when ns_writer is NULL
will cause recovery write to fail.  The purpose of using the cleanup-only
flag is to allow for narrowing of such conditions.

## References
- https://git.kernel.org/stable/c/11afd67f1b3c28eb216e50a3ca8dbcb69bb71793
- https://git.kernel.org/stable/c/3645510cf926e6af2f4d44899370d7e5331c93bd
- https://git.kernel.org/stable/c/37207240872456fbab44a110bde6640445233963
- https://git.kernel.org/stable/c/5828d5f5dc877dcfdd7b23102e978e2ecfd86d82
- https://git.kernel.org/stable/c/7532ff6edbf5242376b24a95a2fefb59bb653e5a
- https://git.kernel.org/stable/c/a3c3b4cbf9b8554120fb230e6516e980c6277487
- https://git.kernel.org/stable/c/d2c539c216cce74837a9cf5804eb205939b82227
- https://git.kernel.org/stable/c/f8654743a0e6909dc634cbfad6db6816f10f3399
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53311.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53311
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
