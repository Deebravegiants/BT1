# [H] ext4: fix use-after-free in ext4_orphan_cleanup

## Summary
Severity: High
Advisory: CVE-2022-50673
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2022-50673
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.18, >=6.1.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix use-after-free in ext4_orphan_cleanup

I caught a issue as follows:
==================================================================
 BUG: KASAN: use-after-free in __list_add_valid+0x28/0x1a0
 Read of size 8 at addr ffff88814b13f378 by task mount/710

 CPU: 1 PID: 710 Comm: mount Not tainted 6.1.0-rc3-next #370
 Call Trace:
  <TASK>
  dump_stack_lvl+0x73/0x9f
  print_report+0x25d/0x759
  kasan_report+0xc0/0x120
  __asan_load8+0x99/0x140
  __list_add_valid+0x28/0x1a0
  ext4_orphan_cleanup+0x564/0x9d0 [ext4]
  __ext4_fill_super+0x48e2/0x5300 [ext4]
  ext4_fill_super+0x19f/0x3a0 [ext4]
  get_tree_bdev+0x27b/0x450
  ext4_get_tree+0x19/0x30 [ext4]
  vfs_get_tree+0x49/0x150
  path_mount+0xaae/0x1350
  do_mount+0xe2/0x110
  __x64_sys_mount+0xf0/0x190
  do_syscall_64+0x35/0x80
  entry_SYSCALL_64_after_hwframe+0x63/0xcd
  </TASK>
 [...]
==================================================================

Above issue may happen as follows:
-------------------------------------
ext4_fill_super
  ext4_orphan_cleanup
   --- loop1: assume last_orphan is 12 ---
    list_add(&EXT4_I(inode)->i_orphan, &EXT4_SB(sb)->s_orphan)
    ext4_truncate --> return 0
      ext4_inode_attach_jinode --> return -ENOMEM
    iput(inode) --> free inode<12>
   --- loop2: last_orphan is still 12 ---
    list_add(&EXT4_I(inode)->i_orphan, &EXT4_SB(sb)->s_orphan);
    // use inode<12> and trigger UAF

To solve this issue, we need to propagate the return value of
ext4_inode_attach_jinode() appropriately.

## References
- https://git.kernel.org/stable/c/026a4490b5381229a30f23d073b58e8e35ee6858
- https://git.kernel.org/stable/c/7223d5e75f26352354ea2c0ccf8b579821b52adf
- https://git.kernel.org/stable/c/7908b8a541b1578cc61b4da7f19b604a931441da
- https://git.kernel.org/stable/c/7f801a1593cb957f73659732836b2dafbdfc7709
- https://git.kernel.org/stable/c/a71248b1accb2b42e4980afef4fa4a27fa0e36f5
- https://git.kernel.org/stable/c/c2bdbd4c69308835d1b6f6ba74feeccbfe113478
- https://git.kernel.org/stable/c/cf0e0817b0f925b70d101d7014ea81b7094e1159
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50673.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50673
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
