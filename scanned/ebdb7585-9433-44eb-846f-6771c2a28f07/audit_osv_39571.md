# [H] RDMA/mlx4: Fix resource leak on error in mlx4_ib_create_srq()

## Summary
Severity: High
Advisory: CVE-2026-46178
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46178
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx4: Fix resource leak on error in mlx4_ib_create_srq()

Sashiko points out that mlx4_srq_alloc() was not undone during error
unwind, add the missing call to mlx4_srq_free().

## References
- https://git.kernel.org/stable/c/0be6ae614ca7fa53e7389e3c7462ed20abbd4192
- https://git.kernel.org/stable/c/0dbd619716fb07b7de1acd64fec673ee6e1adde7
- https://git.kernel.org/stable/c/388617f44d81604a760742a0b5de292d411e63e3
- https://git.kernel.org/stable/c/53fd4c03558672ccb167754fbacbf045c7ab335c
- https://git.kernel.org/stable/c/5b3b220d54e6a3d77380cb7caa1ef79cb8f4fc94
- https://git.kernel.org/stable/c/c54c7e4cb679c0aaa1cb489b9c3f2cd98e63a44c
- https://git.kernel.org/stable/c/c5dc30da990045105c9762248d23076223e7878a
- https://git.kernel.org/stable/c/e01b8c9286c470b71a38acd320106f2c4f2826a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46178.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
