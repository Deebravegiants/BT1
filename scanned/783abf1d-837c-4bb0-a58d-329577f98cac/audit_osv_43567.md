# [H] RDMA/mlx5: Fix UMR XLT cleanup on ODP populate failure

## Summary
Severity: High
Advisory: CVE-2026-74396
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74396
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx5: Fix UMR XLT cleanup on ODP populate failure

mlx5r_umr_update_xlt() allocates and DMA maps an XLT buffer with
mlx5r_umr_create_xlt(). The buffer is released by the common cleanup path
through mlx5r_umr_unmap_free_xlt().

After mlx5_odp_populate_xlt() became fallible, its error path returned
directly and skipped that cleanup. This leaks the XLT DMA mapping and
buffer. If the emergency XLT page was used, it also leaves
xlt_emergency_page_mutex locked.

Break out of the loop so execution falls through the existing cleanup path.

## References
- https://git.kernel.org/stable/c/1eae35b37923cb71b0cb5136d00671440d488b9f
- https://git.kernel.org/stable/c/9619909d4869afe720904c6888a289b9ac3055b8
- https://git.kernel.org/stable/c/ffa85a2c197935ace6f1634ad9eb0a44bc615670
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74396.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74396
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
