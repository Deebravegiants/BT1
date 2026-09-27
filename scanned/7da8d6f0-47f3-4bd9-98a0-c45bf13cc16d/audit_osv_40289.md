# [H] RDMA: During rereg_mr ensure that REREG_ACCESS is compatible

## Summary
Severity: High
Advisory: CVE-2026-52908
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-52908
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA: During rereg_mr ensure that REREG_ACCESS is compatible

If IB_MR_REREG_ACCESS changes from RO to RW then the umem has to be
re-evaluated to ensure it is properly pinned as RW. Since the umem is
hidden inside each driver's mr struct add a ib_umem_check_rereg() function
that each driver has to call before processing IB_MR_REREG_ACCESS.

mlx4 has to retain its duplicate ib_access_writable check because it
implements IB_MR_REREG_ACCESS | IB_MR_REREG_TRANS by changing both items
in place sequentially while the MR is live, so it will continue to not
support this combination.

## References
- https://git.kernel.org/stable/c/09dc18894148381d3bfc550083b1236043870dce
- https://git.kernel.org/stable/c/2904e985a2917b5dac65df82733065e78a65fc9d
- https://git.kernel.org/stable/c/50334a05a950840b39a1ce3d2a173b4183db9b3e
- https://git.kernel.org/stable/c/badad6fad60def1b9805559dd81dbab3d97b82aa
- https://git.kernel.org/stable/c/eba5df21eda0fe7418efbea2f799f8ea1b8ca94c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52908.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
