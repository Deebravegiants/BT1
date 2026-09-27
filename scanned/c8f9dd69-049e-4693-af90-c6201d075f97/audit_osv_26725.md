# [H] ext4: fix use-after-free read in ext4_find_extent for bigalloc + inline

## Summary
Severity: High
Advisory: CVE-2023-53692
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53692
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.271, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix use-after-free read in ext4_find_extent for bigalloc + inline

Syzbot found the following issue:
loop0: detected capacity change from 0 to 2048
EXT4-fs (loop0): mounted filesystem 00000000-0000-0000-0000-000000000000 without journal. Quota mode: none.
==================================================================
BUG: KASAN: use-after-free in ext4_ext_binsearch_idx fs/ext4/extents.c:768 [inline]
BUG: KASAN: use-after-free in ext4_find_extent+0x76e/0xd90 fs/ext4/extents.c:931
Read of size 4 at addr ffff888073644750 by task syz-executor420/5067

CPU: 0 PID: 5067 Comm: syz-executor420 Not tainted 6.2.0-rc1-syzkaller #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 10/26/2022
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x1b1/0x290 lib/dump_stack.c:106
 print_address_description+0x74/0x340 mm/kasan/report.c:306
 print_report+0x107/0x1f0 mm/kasan/report.c:417
 kasan_report+0xcd/0x100 mm/kasan/report.c:517
 ext4_ext_binsearch_idx fs/ext4/extents.c:768 [inline]
 ext4_find_extent+0x76e/0xd90 fs/ext4/extents.c:931
 ext4_clu_mapped+0x117/0x970 fs/ext4/extents.c:5809
 ext4_insert_delayed_block fs/ext4/inode.c:1696 [inline]
 ext4_da_map_blocks fs/ext4/inode.c:1806 [inline]
 ext4_da_get_block_prep+0x9e8/0x13c0 fs/ext4/inode.c:1870
 ext4_block_write_begin+0x6a8/0x2290 fs/ext4/inode.c:1098
 ext4_da_write_begin+0x539/0x760 fs/ext4/inode.c:3082
 generic_perform_write+0x2e4/0x5e0 mm/filemap.c:3772
 ext4_buffered_write_iter+0x122/0x3a0 fs/ext4/file.c:285
 ext4_file_write_iter+0x1d0/0x18f0
 call_write_iter include/linux/fs.h:2186 [inline]
 new_sync_write fs/read_write.c:491 [inline]
 vfs_write+0x7dc/0xc50 fs/read_write.c:584
 ksys_write+0x177/0x2a0 fs/read_write.c:637
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd
RIP: 0033:0x7f4b7a9737b9
RSP: 002b:00007ffc5cac3668 EFLAGS: 00000246 ORIG_RAX: 0000000000000001
RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 00007f4b7a9737b9
RDX: 00000000175d9003 RSI: 0000000020000200 RDI: 0000000000000004
RBP: 00007f4b7a933050 R08: 0000000000000000 R09: 0000000000000000
R10: 000000000000079f R11: 0000000000000246 R12: 00007f4b7a9330e0
R13: 0000000000000000 R14: 0000000000000000 R15: 0000000000000000
 </TASK>

Above issue is happens when enable bigalloc and inline data feature. As
commit 131294c35ed6 fixed delayed allocation bug in ext4_clu_mapped for
bigalloc + inline. But it only resolved issue when has inline data, if
inline data has been converted to extent(ext4_da_convert_inline_data_to_extent)
before writepages, there is no EXT4_STATE_MAY_INLINE_DATA flag. However
i_data is still store inline data in this scene. Then will trigger UAF
when find extent.
To resolve above issue, there is need to add judge "ext4_has_inline_data(inode)"
in ext4_clu_mapped().

## References
- https://git.kernel.org/stable/c/0ce15000dee0ecd6f235f925a327803e2ef489c6
- https://git.kernel.org/stable/c/11c87c8df2cae1d6be83c07e59fef0792de73482
- https://git.kernel.org/stable/c/14da044725a3ab10affa3566d29c15737c0e67a4
- https://git.kernel.org/stable/c/40566def189c513be2c694681256d7486cc6e368
- https://git.kernel.org/stable/c/770b0613637f59f3091dda1ff0c23671a5326b9c
- https://git.kernel.org/stable/c/835659598c67907b98cd2aa57bb951dfaf675c69
- https://git.kernel.org/stable/c/96d440bee177669dc0acedca0abd73bae6a9be8b
- https://git.kernel.org/stable/c/a34f6dcb78c654ab905642c1b4e7e5fbb4f0babe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53692.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53692
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
