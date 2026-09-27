# [H] RDMA/hns: Fix UAF for cq async event

## Summary
Severity: High
Advisory: CVE-2024-38545
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38545
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.15.168, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix UAF for cq async event

The refcount of CQ is not protected by locks. When CQ asynchronous
events and CQ destruction are concurrent, CQ may have been released,
which will cause UAF.

Use the xa_lock() to protect the CQ refcount.

## References
- https://git.kernel.org/stable/c/330c825e66ef65278e4ebe57fd49c1d6f3f4e34e
- https://git.kernel.org/stable/c/37a7559dc1358a8d300437e99ed8ecdab0671507
- https://git.kernel.org/stable/c/39d26cf46306bdc7ae809ecfdbfeff5aa1098911
- https://git.kernel.org/stable/c/63da190eeb5c9d849b71f457b15b308c94cbaf08
- https://git.kernel.org/stable/c/763780ef0336a973e933e40e919339381732dcaf
- https://git.kernel.org/stable/c/a942ec2745ca864cd8512142100e4027dc306a42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38545.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38545
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
