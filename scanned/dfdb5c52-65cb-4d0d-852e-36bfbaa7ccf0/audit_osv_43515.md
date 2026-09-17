# [H] RDMA/mlx5: Fix undefined shift of user RQ WQE size

## Summary
Severity: High
Advisory: CVE-2026-74297
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74297
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx5: Fix undefined shift of user RQ WQE size

set_rq_size() computes the RQ WQE size as "1 << rq_wqe_shift" based on
the user-provided rq_wqe_shift, which is only checked to be greater than
32, so shifts of 32 are still accepted. A shift of 31 also overflows a
signed integer, leading to undefined behavior.

Use check_shl_overflow() to compute the RQ WQE size and reject any
invalid values.

## References
- https://git.kernel.org/stable/c/42f3d2c8c18b92ea33e506a38b64f1a8986c2823
- https://git.kernel.org/stable/c/4b87a2497276a72fd63028e7419abf0fb7ed837b
- https://git.kernel.org/stable/c/6fc874fdfb366bfb11c62e6af9a831c8be59ddda
- https://git.kernel.org/stable/c/9fff54929cc00849d738faa99f06c32399aeb026
- https://git.kernel.org/stable/c/b732db02a2b04cde393638df19de6251ce62a74e
- https://git.kernel.org/stable/c/b746f949c2ac2b041102836095d6d4a2ef21fa75
- https://git.kernel.org/stable/c/c1dbf52d24a8cb1aa56780ba51b72e7d495f258c
- https://git.kernel.org/stable/c/d881d60223aac8fdc12b227d89c76e131e92a9cd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74297.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74297
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
