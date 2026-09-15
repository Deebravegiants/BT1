# [H] btrfs: initialize inode mapping flags for cached inodes

## Summary
Severity: High
Advisory: CVE-2026-80734
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80734
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: initialize inode mapping flags for cached inodes

[BUG]
When running generic/795 with 8K block size, 4K page size, the test
always fails, triggering some ASSERT()s related to folio size:

  795 (241074): drop_caches: 3
  assertion failed: IS_ALIGNED(start, blocksize) && IS_ALIGNED(end + 1, blocksize), in extent_io.c:1404 (blocksize=8192 root=262 ino=258 start=16826368 end=16830463 mapping min order=0)
  ------------[ cut here ]------------
  kernel BUG at extent_io.c:1404!
  Oops: invalid opcode: 0000 [#1] SMP
  CPU: 8 UID: 0 PID: 241105 Comm: fsstress Tainted: G           OE       7.2.0-rc5-custom+ #442 PREEMPT(full)  f4bfb352566f3949f29c233ce6f735050a03b245
  Tainted: [O]=OOT_MODULE, [E]=UNSIGNED_MODULE
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS unknown 02/02/2022
  RIP: 0010:assert_folio_range.cold+0x3d/0x3f [btrfs]
  Call Trace:
   <TASK>
   btrfs_read_folio+0x9e/0x170 [btrfs 4cd1dd93b341b8ef766643f9512f4a86259567a3]
   prepare_one_folio.constprop.0+0x104/0x2a0 [btrfs 4cd1dd93b341b8ef766643f9512f4a86259567a3]
   btrfs_buffered_write+0x285/0xa50 [btrfs 4cd1dd93b341b8ef766643f9512f4a86259567a3]
   btrfs_do_write_iter+0x1aa/0x210 [btrfs 4cd1dd93b341b8ef766643f9512f4a86259567a3]
   iter_file_splice_write+0x31a/0x540
   direct_splice_actor+0x53/0x170
   splice_direct_to_actor+0xe9/0x240
   do_splice_direct+0x76/0xb0
   vfs_copy_file_range+0x1fd/0x630
   __x64_sys_copy_file_range+0xf9/0x220
   do_syscall_64+0xe1/0x790
   entry_SYSCALL_64_after_hwframe+0x4b/0x53
   </TASK>
  ---[ end trace 0000000000000000 ]---

The ASSERT() itself is added by a later patch.
The crash is triggered with that new debug patch, and without this fix.

[CAUSE]
In the above case, the start 16826368 is properly 8K aligned, but the
end (16830463 + 1) is not 8K aligned.
Furthermore the mapping's minimal folio order is 0, not the expected 1
for 8K block size with 4K page size.

So this means some inodes do not have btrfs_set_inode_mapping_order()
called on it.

The missing btrfs_set_inode_mapping_order() call happens for cached
inodes, through the following events:

- btrfs_create_new_inode() called for inode X
  Which properly sets minimal folio order for the VFS inode.

- btrfs_update_inode() called for inode X
  Which calls btrfs_delayed_update_inode() to create a delayed_node
  into root->delayed_nodes xarray.

- Drop cache/memory pressure, evicting in-memory inode X
  Which evicted the inode X, but delayed_node is still in
  root->delayed_nodes for future reuse.

- btrfs_iget() for inode X called again

  btrfs_iget()
  |- btrfs_iget_locked()
  |  |- iget5_locked_rcu()
  |     Which creates a new vfs_inode for btrfs, whose mapping still
  |     has the minimal order as 0.
  |
  |- btrfs_read_locked_inode()
     |- btrfs_fill_inode()
     |  |- btrfs_get_delayed_node()
     |     Which found out the previous node, and use that delayed
     |     node to initialize the new inode.
     |
     |- filled = true;
     |- if (filled) goto cache_index;
        Which skips the btrfs_update_inode_mapping_flags() and
	btrfs_set_inode_mapping_order() calls.
	So the inode still has minimal folio order set as 0, not
	the required 1.

Thus later page cache read will get a folio whose size is smaller than
block size, as the mapping has its minimal folio order set as 0 not 1,
then trigger the ASSERT().

[FIX]
Move the btrfs_update_inode_mapping_flags() and
btrfs_set_inode_mapping_order() calls under cache_index label,
so that the mapping flags and minimal folio order is always set
no matter if we have a cached inode.

## References
- https://git.kernel.org/stable/c/0d26249671171ab759cb4fdce673554a690fa655
- https://git.kernel.org/stable/c/0ef349734a93227b45f65fc50a3311d1cc5f03e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80734.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80734
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
