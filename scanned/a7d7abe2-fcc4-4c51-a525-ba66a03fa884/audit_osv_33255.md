# [H] iommu/amd/pgtbl: Fix possible race while increase page table level

## Summary
Severity: High
Advisory: CVE-2025-39961
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-39961
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/amd/pgtbl: Fix possible race while increase page table level

The AMD IOMMU host page table implementation supports dynamic page table levels
(up to 6 levels), starting with a 3-level configuration that expands based on
IOVA address. The kernel maintains a root pointer and current page table level
to enable proper page table walks in alloc_pte()/fetch_pte() operations.

The IOMMU IOVA allocator initially starts with 32-bit address and onces its
exhuasted it switches to 64-bit address (max address is determined based
on IOMMU and device DMA capability). To support larger IOVA, AMD IOMMU
driver increases page table level.

But in unmap path (iommu_v1_unmap_pages()), fetch_pte() reads
pgtable->[root/mode] without lock. So its possible that in exteme corner case,
when increase_address_space() is updating pgtable->[root/mode], fetch_pte()
reads wrong page table level (pgtable->mode). It does compare the value with
level encoded in page table and returns NULL. This will result is
iommu_unmap ops to fail and upper layer may retry/log WARN_ON.

CPU 0                                         CPU 1
------                                       ------
map pages                                    unmap pages
alloc_pte() -> increase_address_space()      iommu_v1_unmap_pages() -> fetch_pte()
  pgtable->root = pte (new root value)
                                             READ pgtable->[mode/root]
					       Reads new root, old mode
  Updates mode (pgtable->mode += 1)

Since Page table level updates are infrequent and already synchronized with a
spinlock, implement seqcount to enable lock-free read operations on the read path.

## References
- https://git.kernel.org/stable/c/075abf0b1a958acfbea2435003d228e738e90346
- https://git.kernel.org/stable/c/1e56310b40fd2e7e0b9493da9ff488af145bdd0c
- https://git.kernel.org/stable/c/7d462bdecb7d9c32934dab44aaeb7ea7d73a27a2
- https://git.kernel.org/stable/c/cd92c8ab336c3a633d46e6f35ebcd3509ae7db3b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39961.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39961
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
