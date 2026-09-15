# [H] mm/huge_memory: unlock i_mmap_rwsem before releasing after-split folios

## Summary
Severity: High
Advisory: CVE-2026-74482
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74482
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/huge_memory: unlock i_mmap_rwsem before releasing after-split folios

__folio_split() keeps dereferencing the mapping after the split:
shmem_uncharge(mapping->host) and remap_page() while the folios are still
frozen/locked, and i_mmap_unlock_read(mapping) at the very end, after the
after-split folios have been unlocked and freed.

Nothing holds an inode reference across that.  The split relies on @folio
-- which the beyond-EOF drop loop never removes, as it starts at
folio_next(folio) -- staying locked and in the page cache to hold off
eviction.  But the unlock loop unlocks @folio before i_mmap_unlock_read()
runs.  If the caller's @lock_at is a tail beyond EOF, as memory_failure()
passes when splitting a poisoned tail of a shmem THP that reaches past
i_size during truncation, it too is gone from the page cache; so once
@folio is unlocked no locked, in-cache folio pins the inode, and a
concurrent final iput() can evict and RCU-free it before
i_mmap_unlock_read() touches i_mmap_rwsem:

  BUG: KASAN: slab-use-after-free in __up_read+0x634/0x790
   i_mmap_unlock_read include/linux/fs.h:537 [inline]
   __folio_split+0x732/0x1640 mm/huge_memory.c:4100
   try_to_split_thp_page+0xab/0x390 mm/memory-failure.c:1675
   memory_failure+0x1394/0x26e0 mm/memory-failure.c:2470

  Freed by task 4601:
   shmem_free_in_core_inode+0x54/0xb0 mm/shmem.c:5177
   evict+0x57f/0xac0 fs/inode.c:870

Do every mapping dereference while @folio still pins the inode: drop
i_mmap_rwsem right after remap_page(), before the loop that unlocks and
frees the after-split folios, and clear @mapping so the exit path does not
unlock it again.  shmem_uncharge() and remap_page() already run before
that point, so after this nothing past the unlock loop touches the inode
or the mapping.

This is now a rule the split depends on, alongside keeping @folio frozen
until the page cache is updated: no inode or mapping dereference once the
after-split folios start being unlocked.

## References
- https://git.kernel.org/stable/c/10065fb891651d9541e7a5a2db84c1e656ece4f9
- https://git.kernel.org/stable/c/6f5c272d71845a669e4c8ee5c72b376e29a0e6e5
- https://git.kernel.org/stable/c/bc2f5eabaaf60ec18da70b619a8fba1bfb7dea3a
- https://git.kernel.org/stable/c/be106f7855f03d3128ed0ce70ba74b484a90b473
- https://git.kernel.org/stable/c/d640efe94d86d3be893d4c19220362546a637e90
- https://git.kernel.org/stable/c/e3dd774dbfd0b5bc2dbd0995221751b1234f8205
- https://git.kernel.org/stable/c/e923bd21058ea02fd0dcd3549d151d143fd036e5
- https://git.kernel.org/stable/c/f87c08060818ebb19bafed37c38244538da25097
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74482.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74482
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
