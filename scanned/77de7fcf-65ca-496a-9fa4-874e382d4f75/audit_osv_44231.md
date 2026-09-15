# [H] iommufd: Take dma_resv lock before dma_buf_unpin() in release path

## Summary
Severity: High
Advisory: CVE-2026-80633
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80633
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Take dma_resv lock before dma_buf_unpin() in release path

dma_buf_unpin() requires the caller to hold the exporter's dma_resv
lock:

  void dma_buf_unpin(struct dma_buf_attachment *attach)
  {
          ...
          dma_resv_assert_held(dmabuf->resv);
          ...
  }

iopt_release_pages() calls dma_buf_unpin() without taking that lock,
so every iommufd_ioas_destroy()/iommufd_ioas_unmap() that releases
the last reference on a DMABUF-backed iopt_pages triggers a WARN.
This was hit while running tools/testing/selftests/iommu/iommufd:

  WARNING: drivers/dma-buf/dma-buf.c:1137 at dma_buf_unpin+0x62/0x70
  RIP: 0010:dma_buf_unpin+0x62/0x70
  Call Trace:
   <TASK>
   dma_buf_unpin+0x62/0x70
   iopt_release_pages+0xe4/0x190
   iopt_unmap_iova_range+0x1c7/0x290
   iopt_unmap_all+0x1a/0x30
   iommufd_ioas_destroy+0x1d/0x50
   iommufd_fops_release+0x93/0x150
   __fput+0xfc/0x2c0
   __x64_sys_close+0x3d/0x80
   do_syscall_64+0x65/0x180
   </TASK>

Take the dma_resv lock around dma_buf_unpin() in iopt_release_pages(),
matching the iopt_map_dmabuf() convention. dma_buf_detach() acquires the
reservation lock internally, so it must remain outside the locked region.

## References
- https://git.kernel.org/stable/c/cc69d0332421fd2943b66dbe5e597bf4fd5af126
- https://git.kernel.org/stable/c/e745cd2c749e557c14a15ac931761c3f58c24489
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80633.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80633
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
