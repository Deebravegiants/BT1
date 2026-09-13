# [H] nvmem: zynqmp_nvmem: Fix buffer size in DMA and memcpy

## Summary
Severity: High
Advisory: CVE-2026-31743
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31743
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmem: zynqmp_nvmem: Fix buffer size in DMA and memcpy

Buffer size used in dma allocation and memcpy is wrong.
It can lead to undersized DMA buffer access and possible
memory corruption. use correct buffer size in dma_alloc_coherent
and memcpy.

## References
- https://git.kernel.org/stable/c/2f6e5b9964d0a63a5ba84fca2642876afb70a662
- https://git.kernel.org/stable/c/6c01e7f11f5e5f22285d19510a9643e2506e13c3
- https://git.kernel.org/stable/c/784ed4abded1ca4b525fa4cade8b02f8c5d2a087
- https://git.kernel.org/stable/c/f9b88613ff402aa6fe8fd020573cb95867ae947e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31743.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31743
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
