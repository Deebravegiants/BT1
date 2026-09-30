# [M] CVE-2021-47638

## Summary
Severity: Medium
Advisory: CVE-2021-47638
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47638
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: rename_whiteout: Fix double free for whiteout_ui->data

'whiteout_ui->data' will be freed twice if space budget fail for
rename whiteout operation as following process:

rename_whiteout
  dev = kmalloc
  whiteout_ui->data = dev
  kfree(whiteout_ui->data)  // Free first time
  iput(whiteout)
    ubifs_free_inode
      kfree(ui->data)	    // Double free!

KASAN reports:
==================================================================
BUG: KASAN: double-free or invalid-free in ubifs_free_inode+0x4f/0x70
Call Trace:
  kfree+0x117/0x490
  ubifs_free_inode+0x4f/0x70 [ubifs]
  i_callback+0x30/0x60
  rcu_do_batch+0x366/0xac0
  __do_softirq+0x133/0x57f

Allocated by task 1506:
  kmem_cache_alloc_trace+0x3c2/0x7a0
  do_rename+0x9b7/0x1150 [ubifs]
  ubifs_rename+0x106/0x1f0 [ubifs]
  do_syscall_64+0x35/0x80

Freed by task 1506:
  kfree+0x117/0x490
  do_rename.cold+0x53/0x8a [ubifs]
  ubifs_rename+0x106/0x1f0 [ubifs]
  do_syscall_64+0x35/0x80

The buggy address belongs to the object at ffff88810238bed8 which
belongs to the cache kmalloc-8 of size 8
==================================================================

Let ubifs_free_inode() free 'whiteout_ui->data'. BTW, delete unused
assignment 'whiteout_ui->data_len = 0', process 'ubifs_evict_inode()
-> ubifs_jnl_delete_inode() -> ubifs_jnl_write_inode()' doesn't need it
(because 'inc_nlink(whiteout)' won't be excuted by 'goto out_release',
 and the nlink of whiteout inode is 0).

## References
- https://git.kernel.org/stable/c/b9a937f096e608b3368c1abc920d4d640ba2c94f
- https://git.kernel.org/stable/c/14276d38c89a170363e90b6ac0a53c3cf61b87fc
- https://git.kernel.org/stable/c/2ad07009c459e56ebdcc089d850d664660fdb742
- https://git.kernel.org/stable/c/2b3236ecf96db7af5836e1366ce39ace8ce832fa
- https://git.kernel.org/stable/c/40a8f0d5e7b3999f096570edab71c345da812e3e
- https://git.kernel.org/stable/c/6d7a158a7363c1f6604aa47ae1a280a5c65123dd
- https://git.kernel.org/stable/c/8b3c7be16f3f4dfd6e15ac651484e59d3fa36274
- https://git.kernel.org/stable/c/a90e2dbe66d2647ff95a0442ad2e86482d977fd8
