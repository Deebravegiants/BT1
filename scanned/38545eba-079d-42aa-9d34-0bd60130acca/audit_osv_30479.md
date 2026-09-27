# [C] net: stmmac: TSO: Fix unbalanced DMA map/unmap for non-paged SKB data

## Summary
Severity: Critical
Advisory: CVE-2024-53058
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53058
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: TSO: Fix unbalanced DMA map/unmap for non-paged SKB data

In case the non-paged data of a SKB carries protocol header and protocol
payload to be transmitted on a certain platform that the DMA AXI address
width is configured to 40-bit/48-bit, or the size of the non-paged data
is bigger than TSO_MAX_BUFF_SIZE on a certain platform that the DMA AXI
address width is configured to 32-bit, then this SKB requires at least
two DMA transmit descriptors to serve it.

For example, three descriptors are allocated to split one DMA buffer
mapped from one piece of non-paged data:
    dma_desc[N + 0],
    dma_desc[N + 1],
    dma_desc[N + 2].
Then three elements of tx_q->tx_skbuff_dma[] will be allocated to hold
extra information to be reused in stmmac_tx_clean():
    tx_q->tx_skbuff_dma[N + 0],
    tx_q->tx_skbuff_dma[N + 1],
    tx_q->tx_skbuff_dma[N + 2].
Now we focus on tx_q->tx_skbuff_dma[entry].buf, which is the DMA buffer
address returned by DMA mapping call. stmmac_tx_clean() will try to
unmap the DMA buffer _ONLY_IF_ tx_q->tx_skbuff_dma[entry].buf
is a valid buffer address.

The expected behavior that saves DMA buffer address of this non-paged
data to tx_q->tx_skbuff_dma[entry].buf is:
    tx_q->tx_skbuff_dma[N + 0].buf = NULL;
    tx_q->tx_skbuff_dma[N + 1].buf = NULL;
    tx_q->tx_skbuff_dma[N + 2].buf = dma_map_single();
Unfortunately, the current code misbehaves like this:
    tx_q->tx_skbuff_dma[N + 0].buf = dma_map_single();
    tx_q->tx_skbuff_dma[N + 1].buf = NULL;
    tx_q->tx_skbuff_dma[N + 2].buf = NULL;

On the stmmac_tx_clean() side, when dma_desc[N + 0] is closed by the
DMA engine, tx_q->tx_skbuff_dma[N + 0].buf is a valid buffer address
obviously, then the DMA buffer will be unmapped immediately.
There may be a rare case that the DMA engine does not finish the
pending dma_desc[N + 1], dma_desc[N + 2] yet. Now things will go
horribly wrong, DMA is going to access a unmapped/unreferenced memory
region, corrupted data will be transmited or iommu fault will be
triggered :(

In contrast, the for-loop that maps SKB fragments behaves perfectly
as expected, and that is how the driver should do for both non-paged
data and paged frags actually.

This patch corrects DMA map/unmap sequences by fixing the array index
for tx_q->tx_skbuff_dma[entry].buf when assigning DMA buffer address.

Tested and verified on DWXGMAC CORE 3.20a

## References
- https://git.kernel.org/stable/c/07c9c26e37542486e34d767505e842f48f29c3f6
- https://git.kernel.org/stable/c/58d23d835eb498336716cca55b5714191a309286
- https://git.kernel.org/stable/c/66600fac7a984dea4ae095411f644770b2561ede
- https://git.kernel.org/stable/c/a3ff23f7c3f0e13f718900803e090fd3997d6bc9
- https://git.kernel.org/stable/c/ece593fc9c00741b682869d3f3dc584d37b7c9df
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53058.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
