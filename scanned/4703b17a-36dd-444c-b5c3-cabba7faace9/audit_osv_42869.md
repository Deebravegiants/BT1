# [C] net: mana: Sync page pool RX frags for CPU

## Summary
Severity: Critical
Advisory: CVE-2026-72064
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72064
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: Sync page pool RX frags for CPU

MANA allocates RX buffers from page pool fragments when frag_count is
greater than 1. In that case the buffers remain DMA mapped by page pool
and the RX completion path does not call dma_unmap_single(). As a result,
the implicit sync-for-CPU normally performed by dma_unmap_single() is
missing before the packet data is passed to the networking stack.

This breaks RX on configurations which require explicit DMA syncing, for
example when booted with swiotlb=force.

Fix this by recording the page pool page and DMA sync offset when the RX
buffer is allocated, and syncing the received packet range for CPU access
before handing the RX buffer to the stack.

## References
- https://git.kernel.org/stable/c/bc650dd5ce6434286b96e2b26a41af81f679cc7c
- https://git.kernel.org/stable/c/c72a0f09c57f92113df69f9b902d11c9e4b132f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72064.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72064
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
