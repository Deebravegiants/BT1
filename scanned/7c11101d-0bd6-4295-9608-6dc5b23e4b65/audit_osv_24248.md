# [H] RDMA/rxe: Fix "kernel NULL pointer dereference" error

## Summary
Severity: High
Advisory: CVE-2022-50671
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2022-50671
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix "kernel NULL pointer dereference" error

When rxe_queue_init in the function rxe_qp_init_req fails,
both qp->req.task.func and qp->req.task.arg are not initialized.

Because of creation of qp fails, the function rxe_create_qp will
call rxe_qp_do_cleanup to handle allocated resource.

Before calling __rxe_do_task, both qp->req.task.func and
qp->req.task.arg should be checked.

## References
- https://git.kernel.org/stable/c/0d773c58d702f0a7c16ee8d69617fd2c28350795
- https://git.kernel.org/stable/c/3b8752f086eb6865cc3662ad13249b03024501e5
- https://git.kernel.org/stable/c/48cd7098e71735ccafa0b3cf27c53924f9cb5b2f
- https://git.kernel.org/stable/c/9c5dd6993c794703e74c6ba17ac78ca0211ef940
- https://git.kernel.org/stable/c/a625ca30eff806395175ebad3ac1399014bdb280
- https://git.kernel.org/stable/c/bb33fa65da77f5f02dbee6f25cebaeedfcd70028
- https://git.kernel.org/stable/c/cdce36a88def550773142a34ef727a830cad96a8
- https://git.kernel.org/stable/c/eca119693010032d6cc6e7e9b4fb2c363c7e12ce
- https://git.kernel.org/stable/c/f2f405af70e6f0419e718d23fa304798a5405c41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50671.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50671
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
