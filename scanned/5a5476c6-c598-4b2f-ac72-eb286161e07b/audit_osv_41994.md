# [H] fpga: dfl-afu: validate DMA mapping length in afu_dma_map_region()

## Summary
Severity: High
Advisory: CVE-2026-64280
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64280
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fpga: dfl-afu: validate DMA mapping length in afu_dma_map_region()

afu_ioctl_dma_map() accepts a 64-bit length from userspace via
DFL_FPGA_PORT_DMA_MAP ioctl without an upper bound check. The value
is passed to afu_dma_pin_pages() where npages is derived as
length >> PAGE_SHIFT and passed to pin_user_pages_fast() which takes
int nr_pages, causing implicit truncation if length is very large.

Validate map.length at the ioctl entry point before calling
afu_dma_map_region(), rejecting values whose page count exceeds
INT_MAX.

## References
- https://git.kernel.org/stable/c/16381bda90b261a656ded0568630c1b857b2ebc8
- https://git.kernel.org/stable/c/5352d488ce4ae5e8c68c080ad4c3a5f084ad5fbc
- https://git.kernel.org/stable/c/59070040fd12e0b78d7b4d341d9f9a183237c5ff
- https://git.kernel.org/stable/c/a6a3884ff500f04f3088d6d09eec803cd35331a2
- https://git.kernel.org/stable/c/b50e6cd2395cde615f59b624819998d28c0668d6
- https://git.kernel.org/stable/c/d7e787eee2ea619b6dbb98890472ee73daf2e7fd
- https://git.kernel.org/stable/c/fb2c0eab51ae5b02d2bae7d67c2cfbec39b57231
- https://git.kernel.org/stable/c/fc3b071a7c8dc0f5d56defddf6e6fd5aaa3e1e27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64280.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
