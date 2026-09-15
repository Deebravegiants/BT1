# [C] net: stmmac: fix TSO DMA API usage causing oops

## Summary
Severity: Critical
Advisory: CVE-2024-56719
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56719
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: fix TSO DMA API usage causing oops

Commit 66600fac7a98 ("net: stmmac: TSO: Fix unbalanced DMA map/unmap
for non-paged SKB data") moved the assignment of tx_skbuff_dma[]'s
members to be later in stmmac_tso_xmit().

The buf (dma cookie) and len stored in this structure are passed to
dma_unmap_single() by stmmac_tx_clean(). The DMA API requires that
the dma cookie passed to dma_unmap_single() is the same as the value
returned from dma_map_single(). However, by moving the assignment
later, this is not the case when priv->dma_cap.addr64 > 32 as "des"
is offset by proto_hdr_len.

This causes problems such as:

  dwc-eth-dwmac 2490000.ethernet eth0: Tx DMA map failed

and with DMA_API_DEBUG enabled:

  DMA-API: dwc-eth-dwmac 2490000.ethernet: device driver tries to +free DMA memory it has not allocated [device address=0x000000ffffcf65c0] [size=66 bytes]

Fix this by maintaining "des" as the original DMA cookie, and use
tso_des to pass the offset DMA cookie to stmmac_tso_allocator().

Full details of the crashes can be found at:
https://lore.kernel.org/all/d8112193-0386-4e14-b516-37c2d838171a@nvidia.com/
https://lore.kernel.org/all/klkzp5yn5kq5efgtrow6wbvnc46bcqfxs65nz3qy77ujr5turc@bwwhelz2l4dw/

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/05968b6dd0ffc65d7386608b11a11fb4fdfc9f36
- https://git.kernel.org/stable/c/4c49f38e20a57f8abaebdf95b369295b153d1f8e
- https://git.kernel.org/stable/c/6abcdc9a73274052a9e96a1926994ecf9aedad82
- https://git.kernel.org/stable/c/9d5dd7ccea1b46a9a7c6b3c2b9e5ed8864e185e2
- https://git.kernel.org/stable/c/db3667c9bbfbbf5de98e6c9542f7e03fb5243286
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56719.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56719
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
