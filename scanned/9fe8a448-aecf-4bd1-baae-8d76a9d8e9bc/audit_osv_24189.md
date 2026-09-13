# [H] drm/amdgpu: SDMA update use unlocked iterator

## Summary
Severity: High
Advisory: CVE-2022-50393
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50393
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: SDMA update use unlocked iterator

SDMA update page table may be called from unlocked context, this
generate below warning. Use unlocked iterator to handle this case.

WARNING: CPU: 0 PID: 1475 at
drivers/dma-buf/dma-resv.c:483 dma_resv_iter_next
Call Trace:
 dma_resv_iter_first+0x43/0xa0
 amdgpu_vm_sdma_update+0x69/0x2d0 [amdgpu]
 amdgpu_vm_ptes_update+0x29c/0x870 [amdgpu]
 amdgpu_vm_update_range+0x2f6/0x6c0 [amdgpu]
 svm_range_unmap_from_gpus+0x115/0x300 [amdgpu]
 svm_range_cpu_invalidate_pagetables+0x510/0x5e0 [amdgpu]
 __mmu_notifier_invalidate_range_start+0x1d3/0x230
 unmap_vmas+0x140/0x150
 unmap_region+0xa8/0x110

## References
- https://git.kernel.org/stable/c/3913f0179ba366f7d7d160c506ce00de1602bbc4
- https://git.kernel.org/stable/c/4ff3d517cebe8a29b9f3c302b5292bb1ce291e00
- https://git.kernel.org/stable/c/b892c57a3a04c8de247ab9ee08a0a8cf53290e19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50393.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
