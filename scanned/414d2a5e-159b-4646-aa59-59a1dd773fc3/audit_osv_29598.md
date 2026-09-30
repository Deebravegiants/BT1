# [H] f2fs: fix to do sanity check on F2FS_INLINE_DATA flag in inode during GC

## Summary
Severity: High
Advisory: CVE-2024-44942
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-44942
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.6.47, >=6.7.0 <6.10.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to do sanity check on F2FS_INLINE_DATA flag in inode during GC

syzbot reports a f2fs bug as below:

------------[ cut here ]------------
kernel BUG at fs/f2fs/inline.c:258!
CPU: 1 PID: 34 Comm: kworker/u8:2 Not tainted 6.9.0-rc6-syzkaller-00012-g9e4bc4bcae01 #0
RIP: 0010:f2fs_write_inline_data+0x781/0x790 fs/f2fs/inline.c:258
Call Trace:
 f2fs_write_single_data_page+0xb65/0x1d60 fs/f2fs/data.c:2834
 f2fs_write_cache_pages fs/f2fs/data.c:3133 [inline]
 __f2fs_write_data_pages fs/f2fs/data.c:3288 [inline]
 f2fs_write_data_pages+0x1efe/0x3a90 fs/f2fs/data.c:3315
 do_writepages+0x35b/0x870 mm/page-writeback.c:2612
 __writeback_single_inode+0x165/0x10b0 fs/fs-writeback.c:1650
 writeback_sb_inodes+0x905/0x1260 fs/fs-writeback.c:1941
 wb_writeback+0x457/0xce0 fs/fs-writeback.c:2117
 wb_do_writeback fs/fs-writeback.c:2264 [inline]
 wb_workfn+0x410/0x1090 fs/fs-writeback.c:2304
 process_one_work kernel/workqueue.c:3254 [inline]
 process_scheduled_works+0xa12/0x17c0 kernel/workqueue.c:3335
 worker_thread+0x86d/0xd70 kernel/workqueue.c:3416
 kthread+0x2f2/0x390 kernel/kthread.c:388
 ret_from_fork+0x4d/0x80 arch/x86/kernel/process.c:147
 ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:244

The root cause is: inline_data inode can be fuzzed, so that there may
be valid blkaddr in its direct node, once f2fs triggers background GC
to migrate the block, it will hit f2fs_bug_on() during dirty page
writeback.

Let's add sanity check on F2FS_INLINE_DATA flag in inode during GC,
so that, it can forbid migrating inline_data inode's data block for
fixing.

## References
- https://git.kernel.org/stable/c/26c07775fb5dc74351d1c3a2bc3cdf609b03e49f
- https://git.kernel.org/stable/c/ae00e6536a2dd54b64b39e9a39548870cf835745
- https://git.kernel.org/stable/c/fc01008c92f40015aeeced94750855a7111b6929
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44942.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44942
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
