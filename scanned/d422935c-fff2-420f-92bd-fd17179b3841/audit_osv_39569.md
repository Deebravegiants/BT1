# [H] RDMA/mlx5: Fix error path fall-through in mlx5_ib_dev_res_srq_init()

## Summary
Severity: High
Advisory: CVE-2026-46176
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46176
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.140, >=6.7.0 <6.12.88, >=6.11.0 <6.18.30, >=6.13.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx5: Fix error path fall-through in mlx5_ib_dev_res_srq_init()

mlx5_ib_dev_res_srq_init() allocates two SRQs, s0 and s1. When
ib_create_srq() fails for s1, the error branch destroys s0 but falls
through and unconditionally assigns the freed s0 and the ERR_PTR s1 to
devr->s0 and devr->s1.

This leads to several problems: the lock-free fast path checks
"if (devr->s1) return 0;" and treats the ERR_PTR as already initialised;
users in mlx5_ib_create_qp() dereference the freed SRQ or ERR_PTR via
to_msrq(devr->s0)->msrq.srqn; and mlx5_ib_dev_res_cleanup() dereferences
the ERR_PTR and double-frees s0 on teardown.

Fix by adding the same `goto unlock` in the s1 failure path.

## References
- https://git.kernel.org/stable/c/6fd93142dd1d09000c3750af08270f5792523fe9
- https://git.kernel.org/stable/c/a13c2ac4d480b734342c6fbf8249fc48afd675f3
- https://git.kernel.org/stable/c/b087913ae88256df66620f7ba0a9776716aeef7e
- https://git.kernel.org/stable/c/bc2cf5935b4665172235341163315905197ae91d
- https://git.kernel.org/stable/c/c488df06bd552bb8b6e14fa0cfd5ad986c6e9525
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46176.json
- https://access.redhat.com/errata/RHSA-2026:30848
- https://access.redhat.com/errata/RHSA-2026:33215
- https://access.redhat.com/errata/RHSA-2026:33685
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/security/cve/CVE-2026-46176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46176.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46176
- https://bugzilla.redhat.com/show_bug.cgi?id=2482594
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
