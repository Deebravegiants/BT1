# [H] btrfs: ref-verify: fix use-after-free after invalid ref action

## Summary
Severity: High
Advisory: CVE-2024-56581
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56581
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: ref-verify: fix use-after-free after invalid ref action

At btrfs_ref_tree_mod() after we successfully inserted the new ref entry
(local variable 'ref') into the respective block entry's rbtree (local
variable 'be'), if we find an unexpected action of BTRFS_DROP_DELAYED_REF,
we error out and free the ref entry without removing it from the block
entry's rbtree. Then in the error path of btrfs_ref_tree_mod() we call
btrfs_free_ref_cache(), which iterates over all block entries and then
calls free_block_entry() for each one, and there we will trigger a
use-after-free when we are called against the block entry to which we
added the freed ref entry to its rbtree, since the rbtree still points
to the block entry, as we didn't remove it from the rbtree before freeing
it in the error path at btrfs_ref_tree_mod(). Fix this by removing the
new ref entry from the rbtree before freeing it.

Syzbot report this with the following stack traces:

   BTRFS error (device loop0 state EA):   Ref action 2, root 5, ref_root 0, parent 8564736, owner 0, offset 0, num_refs 18446744073709551615
      __btrfs_mod_ref+0x7dd/0xac0 fs/btrfs/extent-tree.c:2523
      update_ref_for_cow+0x9cd/0x11f0 fs/btrfs/ctree.c:512
      btrfs_force_cow_block+0x9f6/0x1da0 fs/btrfs/ctree.c:594
      btrfs_cow_block+0x35e/0xa40 fs/btrfs/ctree.c:754
      btrfs_search_slot+0xbdd/0x30d0 fs/btrfs/ctree.c:2116
      btrfs_insert_empty_items+0x9c/0x1a0 fs/btrfs/ctree.c:4314
      btrfs_insert_empty_item fs/btrfs/ctree.h:669 [inline]
      btrfs_insert_orphan_item+0x1f1/0x320 fs/btrfs/orphan.c:23
      btrfs_orphan_add+0x6d/0x1a0 fs/btrfs/inode.c:3482
      btrfs_unlink+0x267/0x350 fs/btrfs/inode.c:4293
      vfs_unlink+0x365/0x650 fs/namei.c:4469
      do_unlinkat+0x4ae/0x830 fs/namei.c:4533
      __do_sys_unlinkat fs/namei.c:4576 [inline]
      __se_sys_unlinkat fs/namei.c:4569 [inline]
      __x64_sys_unlinkat+0xcc/0xf0 fs/namei.c:4569
      do_syscall_x64 arch/x86/entry/common.c:52 [inline]
      do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
      entry_SYSCALL_64_after_hwframe+0x77/0x7f
   BTRFS error (device loop0 state EA):   Ref action 1, root 5, ref_root 5, parent 0, owner 260, offset 0, num_refs 1
      __btrfs_mod_ref+0x76b/0xac0 fs/btrfs/extent-tree.c:2521
      update_ref_for_cow+0x96a/0x11f0
      btrfs_force_cow_block+0x9f6/0x1da0 fs/btrfs/ctree.c:594
      btrfs_cow_block+0x35e/0xa40 fs/btrfs/ctree.c:754
      btrfs_search_slot+0xbdd/0x30d0 fs/btrfs/ctree.c:2116
      btrfs_lookup_inode+0xdc/0x480 fs/btrfs/inode-item.c:411
      __btrfs_update_delayed_inode+0x1e7/0xb90 fs/btrfs/delayed-inode.c:1030
      btrfs_update_delayed_inode fs/btrfs/delayed-inode.c:1114 [inline]
      __btrfs_commit_inode_delayed_items+0x2318/0x24a0 fs/btrfs/delayed-inode.c:1137
      __btrfs_run_delayed_items+0x213/0x490 fs/btrfs/delayed-inode.c:1171
      btrfs_commit_transaction+0x8a8/0x3740 fs/btrfs/transaction.c:2313
      prepare_to_relocate+0x3c4/0x4c0 fs/btrfs/relocation.c:3586
      relocate_block_group+0x16c/0xd40 fs/btrfs/relocation.c:3611
      btrfs_relocate_block_group+0x77d/0xd90 fs/btrfs/relocation.c:4081
      btrfs_relocate_chunk+0x12c/0x3b0 fs/btrfs/volumes.c:3377
      __btrfs_balance+0x1b0f/0x26b0 fs/btrfs/volumes.c:4161
      btrfs_balance+0xbdc/0x10c0 fs/btrfs/volumes.c:4538
   BTRFS error (device loop0 state EA):   Ref action 2, root 5, ref_root 0, parent 8564736, owner 0, offset 0, num_refs 18446744073709551615
      __btrfs_mod_ref+0x7dd/0xac0 fs/btrfs/extent-tree.c:2523
      update_ref_for_cow+0x9cd/0x11f0 fs/btrfs/ctree.c:512
      btrfs_force_cow_block+0x9f6/0x1da0 fs/btrfs/ctree.c:594
      btrfs_cow_block+0x35e/0xa40 fs/btrfs/ctree.c:754
      btrfs_search_slot+0xbdd/0x30d0 fs/btrfs/ctree.c:2116
      btrfs_lookup_inode+0xdc/0x480 fs/btrfs/inode-item.c:411
      __btrfs_update_delayed_inode+0x1e7/0xb90 fs/btrfs/delayed-inode.c:1030
      btrfs_update_delayed_i
---truncated---

## References
- https://git.kernel.org/stable/c/4275ac2741941c9c7c2293619fdbacb9f70ba85b
- https://git.kernel.org/stable/c/6370db28af9a8ae3bbdfe97f8a48f8f995e144cf
- https://git.kernel.org/stable/c/6fd018aa168e472ce35be32296d109db6adb87ea
- https://git.kernel.org/stable/c/7c4e39f9d2af4abaf82ca0e315d1fd340456620f
- https://git.kernel.org/stable/c/a6f9e7a0bf1185c9070c0de03bb85eafb9abd650
- https://git.kernel.org/stable/c/d2b85ce0561fde894e28fa01bd5d32820d585006
- https://git.kernel.org/stable/c/dfb9fe7de61f34cc241ab3900bdde93341096e0e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56581.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
