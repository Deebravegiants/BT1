# [H] RDMA/irdma: Fix out-of-bounds write in irdma_copy_user_pgaddrs

## Summary
Severity: High
Advisory: CVE-2026-74390
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74390
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Fix out-of-bounds write in irdma_copy_user_pgaddrs

The irdma_copy_user_pgaddrs function loops through all of the umem DMA
blocks to populate the PBLEs and will stop when either the last DMA
block is reached or palloc->total_cnt is reached. The issue is that
the logic for checking palloc->total_cnt would only work for non-zero
values.

When irdma_setup_pbles is called with lvl==0, it
calls irdma_copy_user_pgaddrs with palloc->total_cnt==0, which means
the only way to break out of the loop is to reach the last umem DMA
block, which means it could end up going beyond the fixed size of 4
iwmr->pgaddrmem array that is used in the lvl==0 case.

In the case of QP/CQ/SRQ rings, the value of lvl is determined by a
separate input (for example, req.cq_pages in the case of a CQ). So,
we must perform explicit checking to ensure we don't overflow the
pgaddrmem array if the user provides a umem that consists of more
blocks than their provided req.cq_pages.

## References
- https://git.kernel.org/stable/c/192a3be0e3759daa24af2841208b074ca6dbaabc
- https://git.kernel.org/stable/c/424d51d33c7541a86934067c2c0538124687fc90
- https://git.kernel.org/stable/c/4780f58672ee6328accd54a95f9c00683477e499
- https://git.kernel.org/stable/c/5ebb3ed757be3e04cf803026004aa0beaeb13e9b
- https://git.kernel.org/stable/c/79a20a8e201a779224b4bf115250a7713bde72c0
- https://git.kernel.org/stable/c/9f8f0d2099e3de1194e37dc933ae0c4206b09aaf
- https://git.kernel.org/stable/c/abd27a977b419d584efa659488c22d2306987b29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
