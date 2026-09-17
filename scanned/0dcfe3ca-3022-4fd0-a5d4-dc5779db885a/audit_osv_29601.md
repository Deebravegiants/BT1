# [H] parisc: fix a possible DMA corruption

## Summary
Severity: High
Advisory: CVE-2024-44949
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44949
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <6.1.119, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

parisc: fix a possible DMA corruption

ARCH_DMA_MINALIGN was defined as 16 - this is too small - it may be
possible that two unrelated 16-byte allocations share a cache line. If
one of these allocations is written using DMA and the other is written
using cached write, the value that was written with DMA may be
corrupted.

This commit changes ARCH_DMA_MINALIGN to be 128 on PA20 and 32 on PA1.1 -
that's the largest possible cache line size.

As different parisc microarchitectures have different cache line size, we
define arch_slab_minalign(), cache_line_size() and
dma_get_cache_alignment() so that the kernel may tune slab cache
parameters dynamically, based on the detected cache line size.

## References
- https://git.kernel.org/stable/c/00baca74fb5879e5f9034b6156671301f500f8ee
- https://git.kernel.org/stable/c/533de2f470baac40d3bf622fe631f15231a03c9f
- https://git.kernel.org/stable/c/642a0b7453daff0295310774016fcb56d1f5bc7f
- https://git.kernel.org/stable/c/7ae04ba36b381bffe2471eff3a93edced843240f
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44949.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44949
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
