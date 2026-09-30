# [H] iommu/dma-iommu: Fix wrong scatterlist length assignment in P2PDMA path

## Summary
Severity: High
Advisory: CVE-2026-74277
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74277
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/dma-iommu: Fix wrong scatterlist length assignment in P2PDMA path

In iommu_dma_map_sg(), when handling PCI P2PDMA cases, the DMA length
of the current scatterlist segment `s` is incorrectly assigned from the
head entry `sg->length` instead of the current entry `s->length`.

This typo causes all P2PDMA segments in the scatterlist to inherit the
length of the first segment, leading to corrupted DMA lengths for multi-
segment scatterlists.

Fix this by using `s->length` instead of `sg->length`.

## References
- https://git.kernel.org/stable/c/8646f00ce021e49f4f05bc1d4060a0c27b25d0e1
- https://git.kernel.org/stable/c/db50fb87015b955a5a0c155293b2dd40d63a3b9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74277.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
