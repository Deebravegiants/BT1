# [H] LoongArch: Increase ARCH_DMA_MINALIGN up to 16

## Summary
Severity: High
Advisory: CVE-2025-22049
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22049
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: Increase ARCH_DMA_MINALIGN up to 16

ARCH_DMA_MINALIGN is 1 by default, but some LoongArch-specific devices
(such as APBDMA) require 16 bytes alignment. When the data buffer length
is too small, the hardware may make an error writing cacheline. Thus, it
is dangerous to allocate a small memory buffer for DMA. It's always safe
to define ARCH_DMA_MINALIGN as L1_CACHE_BYTES but unnecessary (kmalloc()
need small memory objects). Therefore, just increase it to 16.

## References
- https://git.kernel.org/stable/c/1d0def2d1658666ec1f32c9495df60e7411e3c82
- https://git.kernel.org/stable/c/279ec25c2df49fba1cd9488f2ddd045d9cb2112e
- https://git.kernel.org/stable/c/4103cfe9dcb88010ae4911d3ff417457d1b6a720
- https://git.kernel.org/stable/c/8b82aea3666f8f2c78f86148d78aea99c46e0f82
- https://git.kernel.org/stable/c/bfff341cac7c650e6ca8d10503725992f5564d0f
- https://git.kernel.org/stable/c/f39af67f03b564b763b06e44cb960c10a382d54a
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22049.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22049
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
