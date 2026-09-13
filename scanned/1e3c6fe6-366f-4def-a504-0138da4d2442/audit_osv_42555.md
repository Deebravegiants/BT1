# [H] RDMA/siw: publish QP after initialization

## Summary
Severity: High
Advisory: CVE-2026-68417
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68417
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: publish QP after initialization

siw_create_qp() currently calls siw_qp_add() before the queues, CQ
pointers, state, completion, and device list entry are ready. A QPN
lookup can therefore reach a QP that is still being constructed.

Move siw_qp_add() to the end of siw_create_qp(), after QP
initialization and before adding the QP to the siw device list.

## References
- https://git.kernel.org/stable/c/36e91a58397ca8c978e38a0bf389f0c6113fa8ca
- https://git.kernel.org/stable/c/3c9d128219964dcea897bf6139b88242e987be8f
- https://git.kernel.org/stable/c/3ff82e3841ecab1ff38d5817c969a019d266c83c
- https://git.kernel.org/stable/c/52f9fcb191143448df55fd215ff09c5207fed43e
- https://git.kernel.org/stable/c/74912ad168f87d6b2b670a87987bb302d6e64aa1
- https://git.kernel.org/stable/c/bb27fcc67c429d97f785c92c35a6c5adebb05d7f
- https://git.kernel.org/stable/c/fcc9d50022bcdb1f9f7ed04955c72b4a7355af3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68417.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68417
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
