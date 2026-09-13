# [H] ntfs: avoid stale runlist element dereference in fallocate

## Summary
Severity: High
Advisory: CVE-2026-72353
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72353
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: avoid stale runlist element dereference in fallocate

ntfs_attr_fallocate() allocates holes and delayed allocations inside
initialized size by looking up the current runlist element under
ni->runlist.lock. The returned struct runlist_element is only a borrowed
pointer into ni->runlist.rl. A writer can replace and free that array
after the read lock is dropped, so later reads of rl->lcn, rl->length and
rl->vcn can touch freed memory.

The buggy scenario involves two paths, with each column showing the order
within that path:

ntfs_attr_fallocate():
  1. Take ni->runlist.lock for read.
  2. Get rl from ntfs_attr_find_vcn_nolock().
  3. Drop ni->runlist.lock.
  4. Read rl->lcn, rl->length and rl->vcn.

mmap page_mkwrite:
  1. Enter ntfs_filemap_page_mkwrite().
  2. Reach __ntfs_write_iomap_begin() and ntfs_attr_map_cluster().
  3. Merge allocation state with ntfs_runlists_merge().
  4. Reallocate ni->runlist.rl in ntfs_rl_realloc(), freeing the old array.

Validation reproduced this kernel report:
BUG: KASAN: slab-use-after-free in ntfs_attr_fallocate+0xbb8/0xd00

Call Trace:
 <TASK>
 dump_stack_lvl+0x66/0xa0
 print_report+0xce/0x630
 ? ntfs_attr_fallocate+0xbb8/0xd00
 ? srso_alias_return_thunk+0x5/0xfbef5
 ? __virt_addr_valid+0x20d/0x410
 ? ntfs_attr_fallocate+0xbb8/0xd00
 kasan_report+0xe0/0x110
 ? ntfs_attr_fallocate+0xbb8/0xd00
 ntfs_attr_fallocate+0xbb8/0xd00
 ? lock_acquire+0x2b8/0x2f0
 ? __pfx_ntfs_attr_fallocate+0x10/0x10
 ? 0xffffffffc0000095
 ? down_write+0x10d/0x1e0
 ntfs_fallocate+0x5c9/0x1d00
 ? __pfx_ntfs_fallocate+0x10/0x10
 ? srso_alias_return_thunk+0x5/0xfbef5
 ? lock_acquire+0x2b8/0x2f0
 ? srso_alias_return_thunk+0x5/0xfbef5
 ? selinux_file_permission+0x3a7/0x510
 vfs_fallocate+0x29d/0xd30
 __x64_sys_fallocate+0xc7/0x150
 ? do_syscall_64+0x81/0x6a0
 do_syscall_64+0x115/0x6a0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Allocated by task 410:
 kasan_save_stack+0x33/0x60
 kasan_save_track+0x14/0x30
 __kasan_kmalloc+0xaa/0xb0
 __kvmalloc_node_noprof+0x353/0x920
 ntfs_rl_realloc+0x3f/0x110
 ntfs_runlists_merge+0xaa3/0x3010
 ntfs_attr_map_cluster+0x4e5/0xf80
 ntfs_attr_fallocate+0x53f/0xd00
 ntfs_fallocate+0x5c9/0x1d00
 vfs_fallocate+0x29d/0xd30
 __x64_sys_fallocate+0xc7/0x150
 do_syscall_64+0x115/0x6a0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Freed by task 424:
 kasan_save_stack+0x33/0x60
 kasan_save_track+0x14/0x30
 kasan_save_free_info+0x3b/0x60
 __kasan_slab_free+0x5f/0x80
 kfree+0x307/0x580
 ntfs_rl_realloc+0x6f/0x110
 ntfs_runlists_merge+0x7b1/0x3010
 ntfs_attr_map_cluster+0x4e5/0xf80
 __ntfs_write_iomap_begin+0x8cd/0x2280
 iomap_iter+0x6de/0x11e0
 iomap_page_mkwrite+0x391/0x650
 ntfs_filemap_page_mkwrite+0x1ac/0x400
 do_page_mkwrite+0x15c/0x280
 __handle_mm_fault+0xd6d/0x1ca0
 handle_mm_fault+0x19c/0x470
 do_user_addr_fault+0x23b/0x9c0
 exc_page_fault+0x5c/0xc0
 asm_exc_page_fault+0x26/0x30

Fix this by copying the needed runlist fields while the read lock is still
held and using only those scalar snapshots after unlocking.

After the snapshot, ntfs_attr_map_cluster() can also find that the range
is already mapped and return balloc=false. Only call ntfs_dio_zero_range()
when new clusters were allocated, matching the write iomap path and
preserving the zero-newly-allocated-holes behavior.

## References
- https://git.kernel.org/stable/c/3dd3e43f17cda174009a51fe668046ed7afef46a
- https://git.kernel.org/stable/c/88496c4ac5a6ade75619f4b1015706a8b924d50a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72353.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72353
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
