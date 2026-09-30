# [H] vfs: fix race between evice_inodes() and find_inode()&iput()

## Summary
Severity: High
Advisory: CVE-2024-47679
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47679
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfs: fix race between evice_inodes() and find_inode()&iput()

Hi, all

Recently I noticed a bug[1] in btrfs, after digged it into
and I believe it'a race in vfs.

Let's assume there's a inode (ie ino 261) with i_count 1 is
called by iput(), and there's a concurrent thread calling
generic_shutdown_super().

cpu0:                              cpu1:
iput() // i_count is 1
  ->spin_lock(inode)
  ->dec i_count to 0
  ->iput_final()                    generic_shutdown_super()
    ->__inode_add_lru()               ->evict_inodes()
      // cause some reason[2]           ->if (atomic_read(inode->i_count)) continue;
      // return before                  // inode 261 passed the above check
      // list_lru_add_obj()             // and then schedule out
   ->spin_unlock()
// note here: the inode 261
// was still at sb list and hash list,
// and I_FREEING|I_WILL_FREE was not been set

btrfs_iget()
  // after some function calls
  ->find_inode()
    // found the above inode 261
    ->spin_lock(inode)
   // check I_FREEING|I_WILL_FREE
   // and passed
      ->__iget()
    ->spin_unlock(inode)                // schedule back
                                        ->spin_lock(inode)
                                        // check (I_NEW|I_FREEING|I_WILL_FREE) flags,
                                        // passed and set I_FREEING
iput()                                  ->spin_unlock(inode)
  ->spin_lock(inode)			  ->evict()
  // dec i_count to 0
  ->iput_final()
    ->spin_unlock()
    ->evict()

Now, we have two threads simultaneously evicting
the same inode, which may trigger the BUG(inode->i_state & I_CLEAR)
statement both within clear_inode() and iput().

To fix the bug, recheck the inode->i_count after holding i_lock.
Because in the most scenarios, the first check is valid, and
the overhead of spin_lock() can be reduced.

If there is any misunderstanding, please let me know, thanks.

[1]: https://lore.kernel.org/linux-btrfs/000000000000eabe1d0619c48986@google.com/
[2]: The reason might be 1. SB_ACTIVE was removed or 2. mapping_shrinkable()
return false when I reproduced the bug.

## References
- https://git.kernel.org/stable/c/0eed942bc65de1f93eca7bda51344290f9c573bb
- https://git.kernel.org/stable/c/0f8a5b6d0dafa4f533ac82e98f8b812073a7c9d1
- https://git.kernel.org/stable/c/3721a69403291e2514d13a7c3af50a006ea1153b
- https://git.kernel.org/stable/c/47a68c75052a660e4c37de41e321582ec9496195
- https://git.kernel.org/stable/c/489faddb1ae75b0e1a741fe5ca2542a2b5e794a5
- https://git.kernel.org/stable/c/540fb13120c9eab3ef203f90c00c8e69f37449d1
- https://git.kernel.org/stable/c/6c857fb12b9137fee574443385d53914356bbe11
- https://git.kernel.org/stable/c/6cc13a80a26e6b48f78c725c01b91987d61563ef
- https://git.kernel.org/stable/c/88b1afbf0f6b221f6c5bb66cc80cd3b38d696687
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47679.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47679
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
