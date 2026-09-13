# [H] iommu/vt-d: Remove cache tags before disabling ATS

## Summary
Severity: High
Advisory: CVE-2024-56669
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56669
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Remove cache tags before disabling ATS

The current implementation removes cache tags after disabling ATS,
leading to potential memory leaks and kernel crashes. Specifically,
CACHE_TAG_DEVTLB type cache tags may still remain in the list even
after the domain is freed, causing a use-after-free condition.

This issue really shows up when multiple VFs from different PFs
passed through to a single user-space process via vfio-pci. In such
cases, the kernel may crash with kernel messages like:

 BUG: kernel NULL pointer dereference, address: 0000000000000014
 PGD 19036a067 P4D 1940a3067 PUD 136c9b067 PMD 0
 Oops: Oops: 0000 [#1] PREEMPT SMP NOPTI
 CPU: 74 UID: 0 PID: 3183 Comm: testCli Not tainted 6.11.9 #2
 RIP: 0010:cache_tag_flush_range+0x9b/0x250
 Call Trace:
  <TASK>
  ? __die+0x1f/0x60
  ? page_fault_oops+0x163/0x590
  ? exc_page_fault+0x72/0x190
  ? asm_exc_page_fault+0x22/0x30
  ? cache_tag_flush_range+0x9b/0x250
  ? cache_tag_flush_range+0x5d/0x250
  intel_iommu_tlb_sync+0x29/0x40
  intel_iommu_unmap_pages+0xfe/0x160
  __iommu_unmap+0xd8/0x1a0
  vfio_unmap_unpin+0x182/0x340 [vfio_iommu_type1]
  vfio_remove_dma+0x2a/0xb0 [vfio_iommu_type1]
  vfio_iommu_type1_ioctl+0xafa/0x18e0 [vfio_iommu_type1]

Move cache_tag_unassign_domain() before iommu_disable_pci_caps() to fix
it.

## References
- https://git.kernel.org/stable/c/1f2557e08a617a4b5e92a48a1a9a6f86621def18
- https://git.kernel.org/stable/c/9a0a72d3ed919ebe6491f527630998be053151d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56669.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
