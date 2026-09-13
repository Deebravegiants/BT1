# [H] f2fs: fix to don't dirty inode for readonly filesystem

## Summary
Severity: High
Advisory: CVE-2024-42297
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42297
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to don't dirty inode for readonly filesystem

syzbot reports f2fs bug as below:

kernel BUG at fs/f2fs/inode.c:933!
RIP: 0010:f2fs_evict_inode+0x1576/0x1590 fs/f2fs/inode.c:933
Call Trace:
 evict+0x2a4/0x620 fs/inode.c:664
 dispose_list fs/inode.c:697 [inline]
 evict_inodes+0x5f8/0x690 fs/inode.c:747
 generic_shutdown_super+0x9d/0x2c0 fs/super.c:675
 kill_block_super+0x44/0x90 fs/super.c:1667
 kill_f2fs_super+0x303/0x3b0 fs/f2fs/super.c:4894
 deactivate_locked_super+0xc1/0x130 fs/super.c:484
 cleanup_mnt+0x426/0x4c0 fs/namespace.c:1256
 task_work_run+0x24a/0x300 kernel/task_work.c:180
 ptrace_notify+0x2cd/0x380 kernel/signal.c:2399
 ptrace_report_syscall include/linux/ptrace.h:411 [inline]
 ptrace_report_syscall_exit include/linux/ptrace.h:473 [inline]
 syscall_exit_work kernel/entry/common.c:251 [inline]
 syscall_exit_to_user_mode_prepare kernel/entry/common.c:278 [inline]
 __syscall_exit_to_user_mode_work kernel/entry/common.c:283 [inline]
 syscall_exit_to_user_mode+0x15c/0x280 kernel/entry/common.c:296
 do_syscall_64+0x50/0x110 arch/x86/entry/common.c:88
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

The root cause is:
- do_sys_open
 - f2fs_lookup
  - __f2fs_find_entry
   - f2fs_i_depth_write
    - f2fs_mark_inode_dirty_sync
     - f2fs_dirty_inode
      - set_inode_flag(inode, FI_DIRTY_INODE)

- umount
 - kill_f2fs_super
  - kill_block_super
   - generic_shutdown_super
    - sync_filesystem
    : sb is readonly, skip sync_filesystem()
    - evict_inodes
     - iput
      - f2fs_evict_inode
       - f2fs_bug_on(sbi, is_inode_flag_set(inode, FI_DIRTY_INODE))
       : trigger kernel panic

When we try to repair i_current_depth in readonly filesystem, let's
skip dirty inode to avoid panic in later f2fs_evict_inode().

## References
- https://git.kernel.org/stable/c/192b8fb8d1c8ca3c87366ebbef599fa80bb626b8
- https://git.kernel.org/stable/c/2434344559f6743efb3ac15d11af9a0db9543bd3
- https://git.kernel.org/stable/c/2d2916516577f2239b3377d9e8d12da5e6ccdfcf
- https://git.kernel.org/stable/c/54162974aea37a8cae00742470a78c7f6bd6f915
- https://git.kernel.org/stable/c/54bc4e88447e385c4d4ffa85d93e0dce628fcfa6
- https://git.kernel.org/stable/c/9ce8135accf103f7333af472709125878704fdd4
- https://git.kernel.org/stable/c/e62ff092a42f4a1bae3b310cf46673b4f3aac3b5
- https://git.kernel.org/stable/c/ec56571b4b146a1cfbedab49d5fcaf19fe8bf4f1
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42297.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42297
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
