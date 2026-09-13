# [C] RDMA/siw: Fix QP destroy to wait for all references dropped.

## Summary
Severity: Critical
Advisory: CVE-2022-50666
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2022-50666
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Fix QP destroy to wait for all references dropped.

Delay QP destroy completion until all siw references to QP are
dropped. The calling RDMA core will free QP structure after
successful return from siw_qp_destroy() call, so siw must not
hold any remaining reference to the QP upon return.
A use-after-free was encountered in xfstest generic/460, while
testing NFSoRDMA. Here, after a TCP connection drop by peer,
the triggered siw_cm_work_handler got delayed until after
QP destroy call, referencing a QP which has already freed.

## References
- https://git.kernel.org/stable/c/0ed8bf9d0bb19f3f5eedd73f04aaf5bba9ac0737
- https://git.kernel.org/stable/c/5c75d608fad58301b63e7d69200c13c3a1d411da
- https://git.kernel.org/stable/c/74ad141e995a730760b1bcfa14854b7f1057d6bc
- https://git.kernel.org/stable/c/a3c278807a459e6f50afee6971cabe74cccfb490
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50666.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50666
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
