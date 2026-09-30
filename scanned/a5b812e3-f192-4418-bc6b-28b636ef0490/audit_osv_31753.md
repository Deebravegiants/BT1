# [H] nilfs2: do not force clear folio if buffer is referenced

## Summary
Severity: High
Advisory: CVE-2025-21722
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21722
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: do not force clear folio if buffer is referenced

Patch series "nilfs2: protect busy buffer heads from being force-cleared".

This series fixes the buffer head state inconsistency issues reported by
syzbot that occurs when the filesystem is corrupted and falls back to
read-only, and the associated buffer head use-after-free issue.


This patch (of 2):

Syzbot has reported that after nilfs2 detects filesystem corruption and
falls back to read-only, inconsistencies in the buffer state may occur.

One of the inconsistencies is that when nilfs2 calls mark_buffer_dirty()
to set a data or metadata buffer as dirty, but it detects that the buffer
is not in the uptodate state:

 WARNING: CPU: 0 PID: 6049 at fs/buffer.c:1177 mark_buffer_dirty+0x2e5/0x520
  fs/buffer.c:1177
 ...
 Call Trace:
  <TASK>
  nilfs_palloc_commit_alloc_entry+0x4b/0x160 fs/nilfs2/alloc.c:598
  nilfs_ifile_create_inode+0x1dd/0x3a0 fs/nilfs2/ifile.c:73
  nilfs_new_inode+0x254/0x830 fs/nilfs2/inode.c:344
  nilfs_mkdir+0x10d/0x340 fs/nilfs2/namei.c:218
  vfs_mkdir+0x2f9/0x4f0 fs/namei.c:4257
  do_mkdirat+0x264/0x3a0 fs/namei.c:4280
  __do_sys_mkdirat fs/namei.c:4295 [inline]
  __se_sys_mkdirat fs/namei.c:4293 [inline]
  __x64_sys_mkdirat+0x87/0xa0 fs/namei.c:4293
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
  entry_SYSCALL_64_after_hwframe+0x77/0x7f

The other is when nilfs_btree_propagate(), which propagates the dirty
state to the ancestor nodes of a b-tree that point to a dirty buffer,
detects that the origin buffer is not dirty, even though it should be:

 WARNING: CPU: 0 PID: 5245 at fs/nilfs2/btree.c:2089
  nilfs_btree_propagate+0xc79/0xdf0 fs/nilfs2/btree.c:2089
 ...
 Call Trace:
  <TASK>
  nilfs_bmap_propagate+0x75/0x120 fs/nilfs2/bmap.c:345
  nilfs_collect_file_data+0x4d/0xd0 fs/nilfs2/segment.c:587
  nilfs_segctor_apply_buffers+0x184/0x340 fs/nilfs2/segment.c:1006
  nilfs_segctor_scan_file+0x28c/0xa50 fs/nilfs2/segment.c:1045
  nilfs_segctor_collect_blocks fs/nilfs2/segment.c:1216 [inline]
  nilfs_segctor_collect fs/nilfs2/segment.c:1540 [inline]
  nilfs_segctor_do_construct+0x1c28/0x6b90 fs/nilfs2/segment.c:2115
  nilfs_segctor_construct+0x181/0x6b0 fs/nilfs2/segment.c:2479
  nilfs_segctor_thread_construct fs/nilfs2/segment.c:2587 [inline]
  nilfs_segctor_thread+0x69e/0xe80 fs/nilfs2/segment.c:2701
  kthread+0x2f0/0x390 kernel/kthread.c:389
  ret_from_fork+0x4b/0x80 arch/x86/kernel/process.c:147
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:244
  </TASK>

Both of these issues are caused by the callbacks that handle the
page/folio write requests, forcibly clear various states, including the
working state of the buffers they hold, at unexpected times when they
detect read-only fallback.

Fix these issues by checking if the buffer is referenced before clearing
the page/folio state, and skipping the clear if it is.

## References
- https://git.kernel.org/stable/c/1098bb8d52419d262a3358d099a1598a920b730f
- https://git.kernel.org/stable/c/19296737024cd220a1d6590bf4c092bca8c99497
- https://git.kernel.org/stable/c/4d042811c72f71be7c14726db2c72b67025a7cb5
- https://git.kernel.org/stable/c/557ccf5e49f1fb848a29698585bcab2e50a597ef
- https://git.kernel.org/stable/c/7d0544bacc11d6aa26ecd7debf9353193c7a3328
- https://git.kernel.org/stable/c/ca76bb226bf47ff04c782cacbd299f12ddee1ec1
- https://git.kernel.org/stable/c/f51ff43c4c5a6c8e72d0aca89e4d5e688938412f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21722.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21722
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
