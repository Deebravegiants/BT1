# [H] RDMA/bnxt_re: Prevent handling any completions after qp destroy

## Summary
Severity: High
Advisory: CVE-2023-54048
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54048
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.15.124, >=5.16.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Prevent handling any completions after qp destroy

HW may generate completions that indicates QP is destroyed.
Driver should not be scheduling any more completion handlers
for this QP, after the QP is destroyed. Since CQs are active
during the QP destroy, driver may still schedule completion
handlers. This can cause a race where the destroy_cq and poll_cq
running simultaneously.

Snippet of kernel panic while doing bnxt_re driver load unload in loop.
This indicates a poll after the CQ is freed. 

[77786.481636] Call Trace:
[77786.481640]  <TASK>
[77786.481644]  bnxt_re_poll_cq+0x14a/0x620 [bnxt_re]
[77786.481658]  ? kvm_clock_read+0x14/0x30
[77786.481693]  __ib_process_cq+0x57/0x190 [ib_core]
[77786.481728]  ib_cq_poll_work+0x26/0x80 [ib_core]
[77786.481761]  process_one_work+0x1e5/0x3f0
[77786.481768]  worker_thread+0x50/0x3a0
[77786.481785]  ? __pfx_worker_thread+0x10/0x10
[77786.481790]  kthread+0xe2/0x110
[77786.481794]  ? __pfx_kthread+0x10/0x10
[77786.481797]  ret_from_fork+0x2c/0x50

To avoid this, complete all completion handlers before returning the
destroy QP. If free_cq is called soon after destroy_qp,  IB stack
will cancel the CQ work before invoking the destroy_cq verb and
this will prevent any race mentioned.

## References
- https://git.kernel.org/stable/c/7faa6097694164380ed19600c7a7993d071270b9
- https://git.kernel.org/stable/c/b5bbc6551297447d3cca55cf907079e206e9cd82
- https://git.kernel.org/stable/c/b79a0e71d6e8692e0b6da05f8aaa7d69191cf7e7
- https://git.kernel.org/stable/c/b8500538b8f5b2cd86b02754c8de83eaa7a2d6ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54048.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
