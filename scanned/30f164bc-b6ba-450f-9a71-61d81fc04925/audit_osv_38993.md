# [H] net: ethernet: ec_bhf: Fix dma_free_coherent() dma handle

## Summary
Severity: High
Advisory: CVE-2026-43283
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43283
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: ec_bhf: Fix dma_free_coherent() dma handle

dma_free_coherent() in error path takes priv->rx_buf.alloc_len as
the dma handle. This would lead to improper unmapping of the buffer.

Change the dma handle to priv->rx_buf.alloc_phys.

## References
- https://git.kernel.org/stable/c/0f589ee54fd6d76d3f75e745f7f12c64cbd749e5
- https://git.kernel.org/stable/c/1b1371cd4032ae859838ebc74215f569987bb197
- https://git.kernel.org/stable/c/1b1d3c5d58a80a19d017a409aa2308162bab5bbf
- https://git.kernel.org/stable/c/1e300c33ef3cc544c2b9c693778fe9490cfe9184
- https://git.kernel.org/stable/c/7e54ff938bebb173822b4c38b33fc164c1cabf92
- https://git.kernel.org/stable/c/8320727be7ff704e07c87624efc2a4a75f54b3ce
- https://git.kernel.org/stable/c/accd0599bc8e73b962247c6c6c70ca7aa1f8e8d0
- https://git.kernel.org/stable/c/ffe68c3766997d82e9ccaf1cdbd47eba269c4aa2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43283.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43283
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
