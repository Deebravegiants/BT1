# [C] net: stmmac: fix integer underflow in chain mode

## Summary
Severity: Critical
Advisory: CVE-2026-31649
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31649
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: fix integer underflow in chain mode

The jumbo_frm() chain-mode implementation unconditionally computes

    len = nopaged_len - bmax;

where nopaged_len = skb_headlen(skb) (linear bytes only) and bmax is
BUF_SIZE_8KiB or BUF_SIZE_2KiB.  However, the caller stmmac_xmit()
decides to invoke jumbo_frm() based on skb->len (total length including
page fragments):

    is_jumbo = stmmac_is_jumbo_frm(priv, skb->len, enh_desc);

When a packet has a small linear portion (nopaged_len <= bmax) but a
large total length due to page fragments (skb->len > bmax), the
subtraction wraps as an unsigned integer, producing a huge len value
(~0xFFFFxxxx).  This causes the while (len != 0) loop to execute
hundreds of thousands of iterations, passing skb->data + bmax * i
pointers far beyond the skb buffer to dma_map_single().  On IOMMU-less
SoCs (the typical deployment for stmmac), this maps arbitrary kernel
memory to the DMA engine, constituting a kernel memory disclosure and
potential memory corruption from hardware.

Fix this by introducing a buf_len local variable clamped to
min(nopaged_len, bmax).  Computing len = nopaged_len - buf_len is then
always safe: it is zero when the linear portion fits within a single
descriptor, causing the while (len != 0) loop to be skipped naturally,
and the fragment loop in stmmac_xmit() handles page fragments afterward.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/10d12b9240ebf96c785f0e2e4228318cd5f3a3eb
- https://git.kernel.org/stable/c/275bdf762e82082f064e60a92448fa2ac43cf95b
- https://git.kernel.org/stable/c/2c91b39912278d0878f9ba60ba04d2518b18a08d
- https://git.kernel.org/stable/c/513e06735f5be575b409d195822195348b164e48
- https://git.kernel.org/stable/c/51f4e090b9f87b40c21b6daadb5c06e6c0a07b67
- https://git.kernel.org/stable/c/6fca757c20396dc2e604dcc61922264e9e3dc803
- https://git.kernel.org/stable/c/a2b68a9a476b9544ff31f1fbcd5d80867a8a5e2f
- https://git.kernel.org/stable/c/b7b8012193fd98236d7ae05d4b553f010a77b2ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31649.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31649
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
