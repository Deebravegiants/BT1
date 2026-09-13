# [C] btrfs: always detect conflicting inodes when logging inode refs

## Summary
Severity: Critical
Advisory: CVE-2025-71183
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-01-31
Source: https://osv.dev/vulnerability/CVE-2025-71183
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: always detect conflicting inodes when logging inode refs

After rename exchanging (either with the rename exchange operation or
regular renames in multiple non-atomic steps) two inodes and at least
one of them is a directory, we can end up with a log tree that contains
only of the inodes and after a power failure that can result in an attempt
to delete the other inode when it should not because it was not deleted
before the power failure. In some case that delete attempt fails when
the target inode is a directory that contains a subvolume inside it, since
the log replay code is not prepared to deal with directory entries that
point to root items (only inode items).

1) We have directories "dir1" (inode A) and "dir2" (inode B) under the
   same parent directory;

2) We have a file (inode C) under directory "dir1" (inode A);

3) We have a subvolume inside directory "dir2" (inode B);

4) All these inodes were persisted in a past transaction and we are
   currently at transaction N;

5) We rename the file (inode C), so at btrfs_log_new_name() we update
   inode C's last_unlink_trans to N;

6) We get a rename exchange for "dir1" (inode A) and "dir2" (inode B),
   so after the exchange "dir1" is inode B and "dir2" is inode A.
   During the rename exchange we call btrfs_log_new_name() for inodes
   A and B, but because they are directories, we don't update their
   last_unlink_trans to N;

7) An fsync against the file (inode C) is done, and because its inode
   has a last_unlink_trans with a value of N we log its parent directory
   (inode A) (through btrfs_log_all_parents(), called from
   btrfs_log_inode_parent()).

8) So we end up with inode B not logged, which now has the old name
   of inode A. At copy_inode_items_to_log(), when logging inode A, we
   did not check if we had any conflicting inode to log because inode
   A has a generation lower than the current transaction (created in
   a past transaction);

9) After a power failure, when replaying the log tree, since we find that
   inode A has a new name that conflicts with the name of inode B in the
   fs tree, we attempt to delete inode B... this is wrong since that
   directory was never deleted before the power failure, and because there
   is a subvolume inside that directory, attempting to delete it will fail
   since replay_dir_deletes() and btrfs_unlink_inode() are not prepared
   to deal with dir items that point to roots instead of inodes.

   When that happens the mount fails and we get a stack trace like the
   following:

   [87.2314] BTRFS info (device dm-0): start tree-log replay
   [87.2318] BTRFS critical (device dm-0): failed to delete reference to subvol, root 5 inode 256 parent 259
   [87.2332] ------------[ cut here ]------------
   [87.2338] BTRFS: Transaction aborted (error -2)
   [87.2346] WARNING: CPU: 1 PID: 638968 at fs/btrfs/inode.c:4345 __btrfs_unlink_inode+0x416/0x440 [btrfs]
   [87.2368] Modules linked in: btrfs loop dm_thin_pool (...)
   [87.2470] CPU: 1 UID: 0 PID: 638968 Comm: mount Tainted: G        W           6.18.0-rc7-btrfs-next-218+ #2 PREEMPT(full)
   [87.2489] Tainted: [W]=WARN
   [87.2494] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.16.2-0-gea1b7a073390-prebuilt.qemu.org 04/01/2014
   [87.2514] RIP: 0010:__btrfs_unlink_inode+0x416/0x440 [btrfs]
   [87.2538] Code: c0 89 04 24 (...)
   [87.2568] RSP: 0018:ffffc0e741f4b9b8 EFLAGS: 00010286
   [87.2574] RAX: 0000000000000000 RBX: ffff9d3ec8a6cf60 RCX: 0000000000000000
   [87.2582] RDX: 0000000000000002 RSI: ffffffff84ab45a1 RDI: 00000000ffffffff
   [87.2591] RBP: ffff9d3ec8a6ef20 R08: 0000000000000000 R09: ffffc0e741f4b840
   [87.2599] R10: ffff9d45dc1fffa8 R11: 0000000000000003 R12: ffff9d3ee26d77e0
   [87.2608] R13: ffffc0e741f4ba98 R14: ffff9d4458040800 R15: ffff9d44b6b7ca10
   [87.2618] FS:  00007f7b9603a840(0000) GS:ffff9d4658982000(0000) knlGS:0000000000000000
   [87.
---truncated---

## References
- https://git.kernel.org/stable/c/0c2413c69129f6ce60157f7b53d9ba880260400b
- https://git.kernel.org/stable/c/7ba0b6461bc4edb3005ea6e00cdae189bcf908a5
- https://git.kernel.org/stable/c/a63998cd6687c14b160dccb0bbcf281b2eb0dab3
- https://git.kernel.org/stable/c/c7f0207db68d5a1b4af23acbef1a8e8ddc431ebb
- https://git.kernel.org/stable/c/d52af58dd463821c5c516aebb031a58934f696ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71183.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71183
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
