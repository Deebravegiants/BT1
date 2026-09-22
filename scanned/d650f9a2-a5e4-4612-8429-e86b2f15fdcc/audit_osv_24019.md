# [M] ext4: fix warning in 'ext4_da_release_space'

## Summary
Severity: Medium
Advisory: CVE-2022-49880
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49880
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.9.333, >=4.10.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix warning in 'ext4_da_release_space'

Syzkaller report issue as follows:
EXT4-fs (loop0): Free/Dirty block details
EXT4-fs (loop0): free_blocks=0
EXT4-fs (loop0): dirty_blocks=0
EXT4-fs (loop0): Block reservation details
EXT4-fs (loop0): i_reserved_data_blocks=0
EXT4-fs warning (device loop0): ext4_da_release_space:1527: ext4_da_release_space: ino 18, to_free 1 with only 0 reserved data blocks
------------[ cut here ]------------
WARNING: CPU: 0 PID: 92 at fs/ext4/inode.c:1528 ext4_da_release_space+0x25e/0x370 fs/ext4/inode.c:1524
Modules linked in:
CPU: 0 PID: 92 Comm: kworker/u4:4 Not tainted 6.0.0-syzkaller-09423-g493ffd6605b2 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/22/2022
Workqueue: writeback wb_workfn (flush-7:0)
RIP: 0010:ext4_da_release_space+0x25e/0x370 fs/ext4/inode.c:1528
RSP: 0018:ffffc900015f6c90 EFLAGS: 00010296
RAX: 42215896cd52ea00 RBX: 0000000000000000 RCX: 42215896cd52ea00
RDX: 0000000000000000 RSI: 0000000080000001 RDI: 0000000000000000
RBP: 1ffff1100e907d96 R08: ffffffff816aa79d R09: fffff520002bece5
R10: fffff520002bece5 R11: 1ffff920002bece4 R12: ffff888021fd2000
R13: ffff88807483ecb0 R14: 0000000000000001 R15: ffff88807483e740
FS:  0000000000000000(0000) GS:ffff8880b9a00000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 00005555569ba628 CR3: 000000000c88e000 CR4: 00000000003506f0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
Call Trace:
 <TASK>
 ext4_es_remove_extent+0x1ab/0x260 fs/ext4/extents_status.c:1461
 mpage_release_unused_pages+0x24d/0xef0 fs/ext4/inode.c:1589
 ext4_writepages+0x12eb/0x3be0 fs/ext4/inode.c:2852
 do_writepages+0x3c3/0x680 mm/page-writeback.c:2469
 __writeback_single_inode+0xd1/0x670 fs/fs-writeback.c:1587
 writeback_sb_inodes+0xb3b/0x18f0 fs/fs-writeback.c:1870
 wb_writeback+0x41f/0x7b0 fs/fs-writeback.c:2044
 wb_do_writeback fs/fs-writeback.c:2187 [inline]
 wb_workfn+0x3cb/0xef0 fs/fs-writeback.c:2227
 process_one_work+0x877/0xdb0 kernel/workqueue.c:2289
 worker_thread+0xb14/0x1330 kernel/workqueue.c:2436
 kthread+0x266/0x300 kernel/kthread.c:376
 ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:306
 </TASK>

Above issue may happens as follows:
ext4_da_write_begin
  ext4_create_inline_data
    ext4_clear_inode_flag(inode, EXT4_INODE_EXTENTS);
    ext4_set_inode_flag(inode, EXT4_INODE_INLINE_DATA);
__ext4_ioctl
  ext4_ext_migrate -> will lead to eh->eh_entries not zero, and set extent flag
ext4_da_write_begin
  ext4_da_convert_inline_data_to_extent
    ext4_da_write_inline_data_begin
      ext4_da_map_blocks
        ext4_insert_delayed_block
	  if (!ext4_es_scan_clu(inode, &ext4_es_is_delonly, lblk))
	    if (!ext4_es_scan_clu(inode, &ext4_es_is_mapped, lblk))
	      ext4_clu_mapped(inode, EXT4_B2C(sbi, lblk)); -> will return 1
	       allocated = true;
          ext4_es_insert_delayed_block(inode, lblk, allocated);
ext4_writepages
  mpage_map_and_submit_extent(handle, &mpd, &give_up_on_write); -> return -ENOSPC
  mpage_release_unused_pages(&mpd, give_up_on_write); -> give_up_on_write == 1
    ext4_es_remove_extent
      ext4_da_release_space(inode, reserved);
        if (unlikely(to_free > ei->i_reserved_data_blocks))
	  -> to_free == 1  but ei->i_reserved_data_blocks == 0
	  -> then trigger warning as above

To solve above issue, forbid inode do migrate which has inline data.

## References
- https://git.kernel.org/stable/c/0a43c015e98121c91a76154edf42280ce1a8a883
- https://git.kernel.org/stable/c/0de5ee103747fd3a24f1c010c79caabe35e8f0bb
- https://git.kernel.org/stable/c/1b8f787ef547230a3249bcf897221ef0cc78481b
- https://git.kernel.org/stable/c/5370b965b7a945bb8f48b9ee23d83a76a947902e
- https://git.kernel.org/stable/c/72743d5598b9096950bbfd6a9b7f173d156eea97
- https://git.kernel.org/stable/c/890d738f569fa9412b70ba09f15407f17a52da20
- https://git.kernel.org/stable/c/89bee03d2fb8c54119b38ac6c24e7d60fae036b6
- https://git.kernel.org/stable/c/c3bf1e95cfa7d950dc3c064d0c2e3d06b427bc63
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49880.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49880
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
