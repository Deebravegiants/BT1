# [H] RDMA/umem: Fix double dma_buf_unpin in failure path

## Summary
Severity: High
Advisory: CVE-2026-43128
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43128
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/umem: Fix double dma_buf_unpin in failure path

In ib_umem_dmabuf_get_pinned_with_dma_device(), the call to
ib_umem_dmabuf_map_pages() can fail. If this occurs, the dmabuf
is immediately unpinned but the umem_dmabuf->pinned flag is still
set. Then, when ib_umem_release() is called, it calls
ib_umem_dmabuf_revoke() which will call dma_buf_unpin() again.

Fix this by removing the immediate unpin upon failure and just let
the ib_umem_release/revoke path handle it. This also ensures the
proper unmap-unpin unwind ordering if the dmabuf_map_pages call
happened to fail due to dma_resv_wait_timeout (and therefore has
a non-NULL umem_dmabuf->sgt).

## References
- https://git.kernel.org/stable/c/104016eb671e19709721c1b0048dd912dc2e96be
- https://git.kernel.org/stable/c/40126bcbefa79ea86672e05dae608596bab38319
- https://git.kernel.org/stable/c/70542b69abff34d24b11ae0bb200cc7a766d18df
- https://git.kernel.org/stable/c/b324327ff6f48d8065dca67eb3b91357e72726bd
- https://git.kernel.org/stable/c/ba3bf0f1bf1d5d0404678485e872980532fcc2c4
- https://git.kernel.org/stable/c/d3e32e2f3262f1b25d77c085ace38e2cc4ad75cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43128.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43128
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
