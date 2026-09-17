# [H] f2fs: fix to avoid UAF in f2fs_sync_inode_meta()

## Summary
Severity: High
Advisory: CVE-2025-38578
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38578
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid UAF in f2fs_sync_inode_meta()

syzbot reported an UAF issue as below: [1] [2]

[1] https://syzkaller.appspot.com/text?tag=CrashReport&x=16594c60580000

==================================================================
BUG: KASAN: use-after-free in __list_del_entry_valid+0xa6/0x130 lib/list_debug.c:62
Read of size 8 at addr ffff888100567dc8 by task kworker/u4:0/8

CPU: 1 PID: 8 Comm: kworker/u4:0 Tainted: G        W          6.1.129-syzkaller-00017-g642656a36791 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 02/12/2025
Workqueue: writeback wb_workfn (flush-7:0)
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x151/0x1b7 lib/dump_stack.c:106
 print_address_description mm/kasan/report.c:316 [inline]
 print_report+0x158/0x4e0 mm/kasan/report.c:427
 kasan_report+0x13c/0x170 mm/kasan/report.c:531
 __asan_report_load8_noabort+0x14/0x20 mm/kasan/report_generic.c:351
 __list_del_entry_valid+0xa6/0x130 lib/list_debug.c:62
 __list_del_entry include/linux/list.h:134 [inline]
 list_del_init include/linux/list.h:206 [inline]
 f2fs_inode_synced+0x100/0x2e0 fs/f2fs/super.c:1553
 f2fs_update_inode+0x72/0x1c40 fs/f2fs/inode.c:588
 f2fs_update_inode_page+0x135/0x170 fs/f2fs/inode.c:706
 f2fs_write_inode+0x416/0x790 fs/f2fs/inode.c:734
 write_inode fs/fs-writeback.c:1460 [inline]
 __writeback_single_inode+0x4cf/0xb80 fs/fs-writeback.c:1677
 writeback_sb_inodes+0xb32/0x1910 fs/fs-writeback.c:1903
 __writeback_inodes_wb+0x118/0x3f0 fs/fs-writeback.c:1974
 wb_writeback+0x3da/0xa00 fs/fs-writeback.c:2081
 wb_check_background_flush fs/fs-writeback.c:2151 [inline]
 wb_do_writeback fs/fs-writeback.c:2239 [inline]
 wb_workfn+0xbba/0x1030 fs/fs-writeback.c:2266
 process_one_work+0x73d/0xcb0 kernel/workqueue.c:2299
 worker_thread+0xa60/0x1260 kernel/workqueue.c:2446
 kthread+0x26d/0x300 kernel/kthread.c:386
 ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:295
 </TASK>

Allocated by task 298:
 kasan_save_stack mm/kasan/common.c:45 [inline]
 kasan_set_track+0x4b/0x70 mm/kasan/common.c:52
 kasan_save_alloc_info+0x1f/0x30 mm/kasan/generic.c:505
 __kasan_slab_alloc+0x6c/0x80 mm/kasan/common.c:333
 kasan_slab_alloc include/linux/kasan.h:202 [inline]
 slab_post_alloc_hook+0x53/0x2c0 mm/slab.h:768
 slab_alloc_node mm/slub.c:3421 [inline]
 slab_alloc mm/slub.c:3431 [inline]
 __kmem_cache_alloc_lru mm/slub.c:3438 [inline]
 kmem_cache_alloc_lru+0x102/0x270 mm/slub.c:3454
 alloc_inode_sb include/linux/fs.h:3255 [inline]
 f2fs_alloc_inode+0x2d/0x350 fs/f2fs/super.c:1437
 alloc_inode fs/inode.c:261 [inline]
 iget_locked+0x18c/0x7e0 fs/inode.c:1373
 f2fs_iget+0x55/0x4ca0 fs/f2fs/inode.c:486
 f2fs_lookup+0x3c1/0xb50 fs/f2fs/namei.c:484
 __lookup_slow+0x2b9/0x3e0 fs/namei.c:1689
 lookup_slow+0x5a/0x80 fs/namei.c:1706
 walk_component+0x2e7/0x410 fs/namei.c:1997
 lookup_last fs/namei.c:2454 [inline]
 path_lookupat+0x16d/0x450 fs/namei.c:2478
 filename_lookup+0x251/0x600 fs/namei.c:2507
 vfs_statx+0x107/0x4b0 fs/stat.c:229
 vfs_fstatat fs/stat.c:267 [inline]
 vfs_lstat include/linux/fs.h:3434 [inline]
 __do_sys_newlstat fs/stat.c:423 [inline]
 __se_sys_newlstat+0xda/0x7c0 fs/stat.c:417
 __x64_sys_newlstat+0x5b/0x70 fs/stat.c:417
 x64_sys_call+0x52/0x9a0 arch/x86/include/generated/asm/syscalls_64.h:7
 do_syscall_x64 arch/x86/entry/common.c:51 [inline]
 do_syscall_64+0x3b/0x80 arch/x86/entry/common.c:81
 entry_SYSCALL_64_after_hwframe+0x68/0xd2

Freed by task 0:
 kasan_save_stack mm/kasan/common.c:45 [inline]
 kasan_set_track+0x4b/0x70 mm/kasan/common.c:52
 kasan_save_free_info+0x2b/0x40 mm/kasan/generic.c:516
 ____kasan_slab_free+0x131/0x180 mm/kasan/common.c:241
 __kasan_slab_free+0x11/0x20 mm/kasan/common.c:249
 kasan_slab_free include/linux/kasan.h:178 [inline]
 slab_free_hook mm/slub.c:1745 [inline]
 slab_free_freelist_hook mm/slub.c:1771 [inline]
 slab_free mm/slub.c:3686 [inline]
 kmem_cache_free+0x
---truncated---

## References
- https://git.kernel.org/stable/c/1edf68272b8cba2b2817ef1488ecb9f0f84cb6a0
- https://git.kernel.org/stable/c/37e78cad7e9e025e63bb35bc200f44637b009bb1
- https://git.kernel.org/stable/c/3d37cadaac1a8e108e576297aab9125b24ea2dfe
- https://git.kernel.org/stable/c/4dcd830c420f2190ae32f03626039fde7b57b2ad
- https://git.kernel.org/stable/c/6cac47af39b2b8edbb41d47c3bd9c332f83e9932
- https://git.kernel.org/stable/c/7c30d79930132466f5be7d0b57add14d1a016bda
- https://git.kernel.org/stable/c/917ae5e280bc263f56c83fba0d0f0be2c4828083
- https://git.kernel.org/stable/c/a4b0cc9e0bba7525a29f37714e88df12a47997a2
- https://git.kernel.org/stable/c/dea243f58a8391e76f42ad5eb59ff210519ee772
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38578.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38578
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
