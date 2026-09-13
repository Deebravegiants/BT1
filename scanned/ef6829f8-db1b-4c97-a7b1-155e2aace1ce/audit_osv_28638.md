# [H] swiotlb: Fix double-allocation of slots due to broken alignment handling

## Summary
Severity: High
Advisory: CVE-2024-35814
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35814
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

swiotlb: Fix double-allocation of slots due to broken alignment handling

Commit bbb73a103fbb ("swiotlb: fix a braino in the alignment check fix"),
which was a fix for commit 0eee5ae10256 ("swiotlb: fix slot alignment
checks"), causes a functional regression with vsock in a virtual machine
using bouncing via a restricted DMA SWIOTLB pool.

When virtio allocates the virtqueues for the vsock device using
dma_alloc_coherent(), the SWIOTLB search can return page-unaligned
allocations if 'area->index' was left unaligned by a previous allocation
from the buffer:

 # Final address in brackets is the SWIOTLB address returned to the caller
 | virtio-pci 0000:00:07.0: orig_addr 0x0 alloc_size 0x2000, iotlb_align_mask 0x800 stride 0x2: got slot 1645-1649/7168 (0x98326800)
 | virtio-pci 0000:00:07.0: orig_addr 0x0 alloc_size 0x2000, iotlb_align_mask 0x800 stride 0x2: got slot 1649-1653/7168 (0x98328800)
 | virtio-pci 0000:00:07.0: orig_addr 0x0 alloc_size 0x2000, iotlb_align_mask 0x800 stride 0x2: got slot 1653-1657/7168 (0x9832a800)

This ends badly (typically buffer corruption and/or a hang) because
swiotlb_alloc() is expecting a page-aligned allocation and so blindly
returns a pointer to the 'struct page' corresponding to the allocation,
therefore double-allocating the first half (2KiB slot) of the 4KiB page.

Fix the problem by treating the allocation alignment separately to any
additional alignment requirements from the device, using the maximum
of the two as the stride to search the buffer slots and taking care
to ensure a minimum of page-alignment for buffers larger than a page.

This also resolves swiotlb allocation failures occuring due to the
inclusion of ~PAGE_MASK in 'iotlb_align_mask' for large allocations and
resulting in alignment requirements exceeding swiotlb_max_mapping_size().

## References
- https://git.kernel.org/stable/c/04867a7a33324c9c562ee7949dbcaab7aaad1fb4
- https://git.kernel.org/stable/c/3e7acd6e25ba77dde48c3b721c54c89cd6a10534
- https://git.kernel.org/stable/c/777391743771040e12cc40d3d0d178f70c616491
- https://git.kernel.org/stable/c/c88668aa6c1da240ea3eb4d128b7906e740d3cb8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35814.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35814
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
