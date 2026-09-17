# [H] dma-buf: heaps: Fix off-by-one in CMA heap fault handler

## Summary
Severity: High
Advisory: CVE-2024-46852
Aliases: A-363259128, ASB-A-363259128
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46852
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.168, >=5.16.0 <6.1.111, >=6.2.0 <6.6.52, >=6.7.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-buf: heaps: Fix off-by-one in CMA heap fault handler

Until VM_DONTEXPAND was added in commit 1c1914d6e8c6 ("dma-buf: heaps:
Don't track CMA dma-buf pages under RssFile") it was possible to obtain
a mapping larger than the buffer size via mremap and bypass the overflow
check in dma_buf_mmap_internal. When using such a mapping to attempt to
fault past the end of the buffer, the CMA heap fault handler also checks
the fault offset against the buffer size, but gets the boundary wrong by
1. Fix the boundary check so that we don't read off the end of the pages
array and insert an arbitrary page in the mapping.

## References
- https://git.kernel.org/stable/c/79cce5e81d20fa9ad553be439d665ac3302d3c95
- https://git.kernel.org/stable/c/84175dc5b2c932266a50c04e5ce342c30f817a2f
- https://git.kernel.org/stable/c/e79050882b857c37634baedbdcf7c2047c24cbff
- https://git.kernel.org/stable/c/ea5ff5d351b520524019f7ff7f9ce418de2dad87
- https://git.kernel.org/stable/c/eb7fc8b65cea22f9038c52398c8b22849e9620ea
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46852.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46852
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
