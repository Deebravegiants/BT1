# [H] ntfs3: init run lock for extend inode

## Summary
Severity: High
Advisory: CVE-2025-68369
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68369
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs3: init run lock for extend inode

After setting the inode mode of $Extend to a regular file, executing the
truncate system call will enter the do_truncate() routine, causing the
run_lock uninitialized error reported by syzbot.

Prior to patch 4e8011ffec79, if the inode mode of $Extend was not set to
a regular file, the do_truncate() routine would not be entered.

Add the run_lock initialization when loading $Extend.

syzbot reported:
INFO: trying to register non-static key.
Call Trace:
 dump_stack_lvl+0x189/0x250 lib/dump_stack.c:120
 assign_lock_key+0x133/0x150 kernel/locking/lockdep.c:984
 register_lock_class+0x105/0x320 kernel/locking/lockdep.c:1299
 __lock_acquire+0x99/0xd20 kernel/locking/lockdep.c:5112
 lock_acquire+0x120/0x360 kernel/locking/lockdep.c:5868
 down_write+0x96/0x1f0 kernel/locking/rwsem.c:1590
 ntfs_set_size+0x140/0x200 fs/ntfs3/inode.c:860
 ntfs_extend+0x1d9/0x970 fs/ntfs3/file.c:387
 ntfs_setattr+0x2e8/0xbe0 fs/ntfs3/file.c:808

## References
- https://git.kernel.org/stable/c/19164d8228317f3f1fe2662a9ba587cfe3b2d29e
- https://git.kernel.org/stable/c/433d1f7c628c3cbdd7efce064d6c7acd072cf6c4
- https://git.kernel.org/stable/c/6e17555728bc469d484c59db4a0abc65c19bc315
- https://git.kernel.org/stable/c/79c8a77b1782e2ace96d063be3c41ba540d1e20a
- https://git.kernel.org/stable/c/907bf69c6b6ce5d038eec7a599d67b45b62624bc
- https://git.kernel.org/stable/c/ab5e8ebeee1caa4fcf8be7d8d62c0a7165469076
- https://git.kernel.org/stable/c/be99c62ac7e7af514e4b13f83c891a3cccefaa48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68369.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68369
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
