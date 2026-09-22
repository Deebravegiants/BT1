# [M] i3c: mipi-i3c-hci: Error out instead on BUG_ON() in IBI DMA setup

## Summary
Severity: Medium
Advisory: CVE-2024-47665
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47665
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

i3c: mipi-i3c-hci: Error out instead on BUG_ON() in IBI DMA setup

Definitely condition dma_get_cache_alignment * defined value > 256
during driver initialization is not reason to BUG_ON(). Turn that to
graceful error out with -EINVAL.

## References
- https://git.kernel.org/stable/c/2666085335bdfedf90d91f4071490ad3980be785
- https://git.kernel.org/stable/c/5a022269abb22809f2a174b90f200fc4b9526058
- https://git.kernel.org/stable/c/8a2be2f1db268ec735419e53ef04ca039fc027dc
- https://git.kernel.org/stable/c/cacb76df247a7cd842ff29755a523b1cba6c0508
- https://git.kernel.org/stable/c/e2d14bfda9eb5393f8a17008afe2aa7fe0a29815
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47665.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47665
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
