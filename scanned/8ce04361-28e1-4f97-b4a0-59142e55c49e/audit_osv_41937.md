# [H] net: devmem: reject dma-buf bind with non-page-aligned size or SG length

## Summary
Severity: High
Advisory: CVE-2026-64124
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64124
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.35, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: devmem: reject dma-buf bind with non-page-aligned size or SG length

net_devmem_bind_dmabuf() trusts dmabuf->size and sg_dma_len() to be
PAGE_SIZE multiples without checking:

  - tx_vec is sized dmabuf->size / PAGE_SIZE, and
    net_devmem_get_niov_at() only bounds-checks virt_addr < dmabuf->size
    before indexing tx_vec[virt_addr / PAGE_SIZE]. With size =
    N*PAGE_SIZE + r (1 <= r < PAGE_SIZE), sendmsg() at iov_base =
    N*PAGE_SIZE passes the bound check and reads tx_vec[N] -- one past.

  - owner->area.num_niovs = len / PAGE_SIZE while gen_pool_add_owner()
    covers the full byte len, so a non-page-multiple non-final sg
    desyncs num_niovs from the gen_pool region for every later sg, on
    both RX and TX.

dma-buf does not require page-aligned sizes, so the bind path has to
enforce what its own indexing assumes. Reject both with -EINVAL.

The size check is TX-only (only tx_vec is sized off dmabuf->size); the
SG-length check covers both directions.

## References
- https://git.kernel.org/stable/c/134c517dfa63203287b2aad6558017f42435a02e
- https://git.kernel.org/stable/c/4eb82ba543421e9e38cc14e4e82058b78850df50
- https://git.kernel.org/stable/c/d5008e4e4ee6b739256b796702a7d1aae1b5c3b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64124.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64124
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
