# [H] ubifs: authentication: Fix use-after-free in ubifs_tnc_end_commit

## Summary
Severity: High
Advisory: CVE-2024-53171
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53171
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: authentication: Fix use-after-free in ubifs_tnc_end_commit

After an insertion in TNC, the tree might split and cause a node to
change its `znode->parent`. A further deletion of other nodes in the
tree (which also could free the nodes), the aforementioned node's
`znode->cparent` could still point to a freed node. This
`znode->cparent` may not be updated when getting nodes to commit in
`ubifs_tnc_start_commit()`. This could then trigger a use-after-free
when accessing the `znode->cparent` in `write_index()` in
`ubifs_tnc_end_commit()`.

This can be triggered by running

  rm -f /etc/test-file.bin
  dd if=/dev/urandom of=/etc/test-file.bin bs=1M count=60 conv=fsync

in a loop, and with `CONFIG_UBIFS_FS_AUTHENTICATION`. KASAN then
reports:

  BUG: KASAN: use-after-free in ubifs_tnc_end_commit+0xa5c/0x1950
  Write of size 32 at addr ffffff800a3af86c by task ubifs_bgt0_20/153

  Call trace:
   dump_backtrace+0x0/0x340
   show_stack+0x18/0x24
   dump_stack_lvl+0x9c/0xbc
   print_address_description.constprop.0+0x74/0x2b0
   kasan_report+0x1d8/0x1f0
   kasan_check_range+0xf8/0x1a0
   memcpy+0x84/0xf4
   ubifs_tnc_end_commit+0xa5c/0x1950
   do_commit+0x4e0/0x1340
   ubifs_bg_thread+0x234/0x2e0
   kthread+0x36c/0x410
   ret_from_fork+0x10/0x20

  Allocated by task 401:
   kasan_save_stack+0x38/0x70
   __kasan_kmalloc+0x8c/0xd0
   __kmalloc+0x34c/0x5bc
   tnc_insert+0x140/0x16a4
   ubifs_tnc_add+0x370/0x52c
   ubifs_jnl_write_data+0x5d8/0x870
   do_writepage+0x36c/0x510
   ubifs_writepage+0x190/0x4dc
   __writepage+0x58/0x154
   write_cache_pages+0x394/0x830
   do_writepages+0x1f0/0x5b0
   filemap_fdatawrite_wbc+0x170/0x25c
   file_write_and_wait_range+0x140/0x190
   ubifs_fsync+0xe8/0x290
   vfs_fsync_range+0xc0/0x1e4
   do_fsync+0x40/0x90
   __arm64_sys_fsync+0x34/0x50
   invoke_syscall.constprop.0+0xa8/0x260
   do_el0_svc+0xc8/0x1f0
   el0_svc+0x34/0x70
   el0t_64_sync_handler+0x108/0x114
   el0t_64_sync+0x1a4/0x1a8

  Freed by task 403:
   kasan_save_stack+0x38/0x70
   kasan_set_track+0x28/0x40
   kasan_set_free_info+0x28/0x4c
   __kasan_slab_free+0xd4/0x13c
   kfree+0xc4/0x3a0
   tnc_delete+0x3f4/0xe40
   ubifs_tnc_remove_range+0x368/0x73c
   ubifs_tnc_remove_ino+0x29c/0x2e0
   ubifs_jnl_delete_inode+0x150/0x260
   ubifs_evict_inode+0x1d4/0x2e4
   evict+0x1c8/0x450
   iput+0x2a0/0x3c4
   do_unlinkat+0x2cc/0x490
   __arm64_sys_unlinkat+0x90/0x100
   invoke_syscall.constprop.0+0xa8/0x260
   do_el0_svc+0xc8/0x1f0
   el0_svc+0x34/0x70
   el0t_64_sync_handler+0x108/0x114
   el0t_64_sync+0x1a4/0x1a8

The offending `memcpy()` in `ubifs_copy_hash()` has a use-after-free
when a node becomes root in TNC but still has a `cparent` to an already
freed node. More specifically, consider the following TNC:

         zroot
         /
        /
      zp1
      /
     /
    zn

Inserting a new node `zn_new` with a key smaller then `zn` will trigger
a split in `tnc_insert()` if `zp1` is full:

         zroot
         /   \
        /     \
      zp1     zp2
      /         \
     /           \
  zn_new          zn

`zn->parent` has now been moved to `zp2`, *but* `zn->cparent` still
points to `zp1`.

Now, consider a removal of all the nodes _except_ `zn`. Just when
`tnc_delete()` is about to delete `zroot` and `zp2`:

         zroot
             \
              \
              zp2
                \
                 \
                 zn

`zroot` and `zp2` get freed and the tree collapses:

           zn

`zn` now becomes the new `zroot`.

`get_znodes_to_commit()` will now only find `zn`, the new `zroot`, and
`write_index()` will check its `znode->cparent` that wrongly points to
the already freed `zp1`. `ubifs_copy_hash()` thus gets wrongly called
with `znode->cparent->zbranch[znode->iip].hash` that triggers the
use-after-free!

Fix this by explicitly setting `znode->cparent` to `NULL` in
`get_znodes_to_commit()` for the root node. The search for the dirty
nodes
---truncated---

## References
- https://git.kernel.org/stable/c/01d3a2293d7e4edfff96618c15727db7e51f11b6
- https://git.kernel.org/stable/c/2497479aecebe869d23a0064e0fd1a03e34f0e2a
- https://git.kernel.org/stable/c/398a91599d263e41c5f95a2fd4ebdb6280b5c6c3
- https://git.kernel.org/stable/c/4617fb8fc15effe8eda4dd898d4e33eb537a7140
- https://git.kernel.org/stable/c/4d9807048b851d7a58d5bd089c16254af896e4df
- https://git.kernel.org/stable/c/74981f7577d183acad1cd58f74c10d263711a215
- https://git.kernel.org/stable/c/8d8b3f5f4cbfbf6cb0ea4a4d5dc296872b4151eb
- https://git.kernel.org/stable/c/daac4aa1825de0dbc1a6eede2fa7f9fc53f14223
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53171.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53171
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
