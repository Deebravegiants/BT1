# [H] mm/hugetlb: fix list corruption in allocate_file_region_entries()

## Summary
Severity: High
Advisory: CVE-2026-74518
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74518
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb: fix list corruption in allocate_file_region_entries()

allocate_file_region_entries() tops up resv->region_cache with freshly
allocated file_region descriptors.  The allocation uses GFP_KERNEL, so
resv->lock is dropped around it: the new entries are gathered on a
stack-local list head, allocated_regions, and spliced into
resv->region_cache once the lock is re-acquired.

The splice used list_splice(), which moves the entries but does not
re-initialize the source head, so allocated_regions is left pointing at an
entry that now lives on resv->region_cache.  The top-up runs in a while
loop that re-checks the cache deficit after re-acquiring the lock.  For a
shared mapping the resv_map is shared by every mapper of the hugetlbfs
inode, so a concurrent region_chg()/region_add()/region_del() on the same
resv_map can consume cache entries during the unlocked window and force a
second iteration.  That iteration calls list_add() on the stale head and
corrupts the list; with CONFIG_DEBUG_LIST the __list_add_valid() check
trips:

  list_add corruption. next->prev should be prev (ffffc900011ff7f8),
  but was ffff88814c281460. (next=ffff88814c545640).
  kernel BUG at lib/list_debug.c:31!
   allocate_file_region_entries+0x191/0x420
   region_chg+0x267/0x300
   hugetlb_reserve_pages+0x387/0xc80
   hugetlbfs_file_mmap+0x2ce/0x3f0
   mmap_region+0x1348/0x1a80
   do_mmap+0x85e/0xb90
   vm_mmap_pgoff+0x18c/0x330
   ksys_mmap_pgoff+0x2a1/0x3e0
   do_syscall_64+0xd7/0x420

Without CONFIG_DEBUG_LIST the bad list_add() silently links a kernel-stack
address into resv->region_cache, leading to later use-after-free.

This was observed as a real host panic on a dense KVM host where a QEMU
guest-RAM hugetlbfs file was mapped MAP_SHARED by both QEMU and a separate
SPDK/DPDK vhost-user target, generating concurrent region_* traffic on one
shared resv_map.

Use list_splice_init() so the source head is re-initialized empty after
each splice, making the retry loop safe.

## References
- https://git.kernel.org/stable/c/01b8569233e47693d6ff7efa96d9854c55f936fc
- https://git.kernel.org/stable/c/126a70bf1a08ddc9d79c471ebdaa2b08cfbab8df
- https://git.kernel.org/stable/c/587a0accc2b4fccc5cf7baf0fe34e50efde51f9c
- https://git.kernel.org/stable/c/62e1c2741a4d923d9854efd5927a6212aad7a187
- https://git.kernel.org/stable/c/9c5fdffc5e1ce84403c58289ee72697051803bf7
- https://git.kernel.org/stable/c/ac1bb7fd45088d0db57a22ce7729f258ebd63cf5
- https://git.kernel.org/stable/c/dd9623f58ec702a07b2d67179d6fcea79c52231a
- https://git.kernel.org/stable/c/f3e54f6a5e1681f83d13e8716bc92ef5ecf121d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74518.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74518
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
