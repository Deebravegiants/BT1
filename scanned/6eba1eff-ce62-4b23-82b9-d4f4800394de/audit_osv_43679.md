# [H] btrfs: zoned: fix deadlock between metadata writeback and transaction commit

## Summary
Severity: High
Advisory: CVE-2026-74572
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74572
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: zoned: fix deadlock between metadata writeback and transaction commit

When writing out metadata extent buffers in a zoned filesystem,
btree_writepages() holds fs_info->zoned_meta_io_lock across the whole
writeback loop, including the call to btrfs_check_meta_write_pointer() ->
check_bg_is_active().

For the tree-log block group, check_bg_is_active() may fail to activate
the zone and fall back to btrfs_zone_finish_one_bg() to free an active
zone. That path waits for the running transaction to commit while still
holding zoned_meta_io_lock, but the committer needs that same lock to
write out the tree extents, so the two tasks deadlock:

  Task A (kworker, metadata writeback)      Task B (fsstress, transaction commit)
  ------------------------------------      -------------------------------------
  wb_workfn()                               btrfs_commit_transaction(T)
   btree_writepages()                        btrfs_write_and_wait_transaction()
    btrfs_zoned_meta_io_lock()                btrfs_write_marked_extents()
    btrfs_check_meta_write_pointer()           btree_writepages()
     check_bg_is_active() [treelog_bg]          btrfs_zoned_meta_io_lock()
      btrfs_zone_finish_one_bg()               <blocks on zoned_meta_io_lock,
       btrfs_zone_finish()                      held by Task A>
        do_zone_finish()
         btrfs_inc_block_group_ro()
          btrfs_wait_for_commit()
           <blocks waiting for commit
            of transaction T, done by
            Task B>

The sibling branch in check_bg_is_active() already drops zoned_meta_io_lock
around do_zone_finish() for this exact reason. Do the same in the tree-log
branch: release the lock around btrfs_zone_finish_one_bg() and re-acquire
it afterwards. The lock only protects fs_info->active_{meta,system}_bg,
which this branch does not touch, and ctx->zoned_bg keeps a reference to
the block group across the unlock, so nothing is lost while the lock
is dropped.

This hang occasionally reproduces with fstests generic/475 on a zoned
btrfs filesystem.

## References
- https://git.kernel.org/stable/c/18577e77c2c8adaadf1f7c6e9bcd1c0b14e5dcdd
- https://git.kernel.org/stable/c/1ebe51c29fa9755d5b2fea28727c051117907cf8
- https://git.kernel.org/stable/c/75859a7cd77cd2ddaddbcb963e3fcd34738953af
- https://git.kernel.org/stable/c/c3320873e0c04ce7b746fc8fe948f07bbbbdec33
- https://git.kernel.org/stable/c/deddd28fd83c264ee2ff5cd6b34449a9f1be6112
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74572.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74572
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
