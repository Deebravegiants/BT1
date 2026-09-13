# [C] block: add pgmap check to biovec_phys_mergeable

## Summary
Severity: Critical
Advisory: CVE-2026-46115
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46115
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: add pgmap check to biovec_phys_mergeable

biovec_phys_mergeable() is used by the request merge, DMA mapping,
and integrity merge paths to decide if two physically contiguous
bvec segments can be coalesced into one. It currently has no check
for whether the segments belong to different dev_pagemaps.

When zone device memory is registered in multiple chunks, each chunk
gets its own dev_pagemap. A single bio can legitimately contain
bvecs from different pgmaps -- iov_iter_extract_bvecs() breaks at
pgmap boundaries but the outer loop in bio_iov_iter_get_pages()
continues filling the same bio. If such bvecs are physically
contiguous, biovec_phys_mergeable() will coalesce them, making it
impossible to recover the correct pgmap for the merged segment
via page_pgmap().

Add a zone_device_pages_have_same_pgmap() check to prevent merging
bvec segments that span different pgmaps.

## References
- https://git.kernel.org/stable/c/13920e4b7b784b40cf4519ff1f0f3e513476a499
- https://git.kernel.org/stable/c/3d2ecbd444b01d6500671d1a582b7393943cf539
- https://git.kernel.org/stable/c/a7f3aa8c9df3905fe820ae36b67ba56b81587574
- https://git.kernel.org/stable/c/f17d521075325b8afc42d1baa1c28a5e9aca111f
- https://git.kernel.org/stable/c/f632dab4b841554cd6416058c61886d7db176581
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46115.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
