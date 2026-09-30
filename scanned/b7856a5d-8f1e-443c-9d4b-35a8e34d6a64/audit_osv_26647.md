# [M] f2fs: don't reset unchangable mount option in f2fs_remount()

## Summary
Severity: Medium
Advisory: CVE-2023-53447
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53447
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: don't reset unchangable mount option in f2fs_remount()

syzbot reports a bug as below:

general protection fault, probably for non-canonical address 0xdffffc0000000009: 0000 [#1] PREEMPT SMP KASAN
RIP: 0010:__lock_acquire+0x69/0x2000 kernel/locking/lockdep.c:4942
Call Trace:
 lock_acquire+0x1e3/0x520 kernel/locking/lockdep.c:5691
 __raw_write_lock include/linux/rwlock_api_smp.h:209 [inline]
 _raw_write_lock+0x2e/0x40 kernel/locking/spinlock.c:300
 __drop_extent_tree+0x3ac/0x660 fs/f2fs/extent_cache.c:1100
 f2fs_drop_extent_tree+0x17/0x30 fs/f2fs/extent_cache.c:1116
 f2fs_insert_range+0x2d5/0x3c0 fs/f2fs/file.c:1664
 f2fs_fallocate+0x4e4/0x6d0 fs/f2fs/file.c:1838
 vfs_fallocate+0x54b/0x6b0 fs/open.c:324
 ksys_fallocate fs/open.c:347 [inline]
 __do_sys_fallocate fs/open.c:355 [inline]
 __se_sys_fallocate fs/open.c:353 [inline]
 __x64_sys_fallocate+0xbd/0x100 fs/open.c:353
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x41/0xc0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

The root cause is race condition as below:
- since it tries to remount rw filesystem, so that do_remount won't
call sb_prepare_remount_readonly to block fallocate, there may be race
condition in between remount and fallocate.
- in f2fs_remount(), default_options() will reset mount option to default
one, and then update it based on result of parse_options(), so there is
a hole which race condition can happen.

Thread A			Thread B
- f2fs_fill_super
 - parse_options
  - clear_opt(READ_EXTENT_CACHE)

- f2fs_remount
 - default_options
  - set_opt(READ_EXTENT_CACHE)
				- f2fs_fallocate
				 - f2fs_insert_range
				  - f2fs_drop_extent_tree
				   - __drop_extent_tree
				    - __may_extent_tree
				     - test_opt(READ_EXTENT_CACHE) return true
				    - write_lock(&et->lock) access NULL pointer
 - parse_options
  - clear_opt(READ_EXTENT_CACHE)

## References
- https://git.kernel.org/stable/c/115557cc226a927924f2d7d1980ccbf6e3b3bb36
- https://git.kernel.org/stable/c/458c15dfbce62c35fefd9ca637b20a051309c9f1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53447.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
