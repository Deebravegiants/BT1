# [C] RDMA/rxe: Fix the warning "__rxe_cleanup+0x12c/0x170 [rdma_rxe]"

## Summary
Severity: Critical
Advisory: CVE-2025-21829
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-21829
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix the warning "__rxe_cleanup+0x12c/0x170 [rdma_rxe]"

The Call Trace is as below:
"
  <TASK>
  ? show_regs.cold+0x1a/0x1f
  ? __rxe_cleanup+0x12c/0x170 [rdma_rxe]
  ? __warn+0x84/0xd0
  ? __rxe_cleanup+0x12c/0x170 [rdma_rxe]
  ? report_bug+0x105/0x180
  ? handle_bug+0x46/0x80
  ? exc_invalid_op+0x19/0x70
  ? asm_exc_invalid_op+0x1b/0x20
  ? __rxe_cleanup+0x12c/0x170 [rdma_rxe]
  ? __rxe_cleanup+0x124/0x170 [rdma_rxe]
  rxe_destroy_qp.cold+0x24/0x29 [rdma_rxe]
  ib_destroy_qp_user+0x118/0x190 [ib_core]
  rdma_destroy_qp.cold+0x43/0x5e [rdma_cm]
  rtrs_cq_qp_destroy.cold+0x1d/0x2b [rtrs_core]
  rtrs_srv_close_work.cold+0x1b/0x31 [rtrs_server]
  process_one_work+0x21d/0x3f0
  worker_thread+0x4a/0x3c0
  ? process_one_work+0x3f0/0x3f0
  kthread+0xf0/0x120
  ? kthread_complete_and_exit+0x20/0x20
  ret_from_fork+0x22/0x30
  </TASK>
"
When too many rdma resources are allocated, rxe needs more time to
handle these rdma resources. Sometimes with the current timeout, rxe
can not release the rdma resources correctly.

Compared with other rdma drivers, a bigger timeout is used.

## References
- https://git.kernel.org/stable/c/45e567800492088bc52c9abac35524b4d332a8f8
- https://git.kernel.org/stable/c/720653309dd31c8a927ef5d87964578ad544980f
- https://git.kernel.org/stable/c/7a2de8126ed3801f2396720e10a03cd546a3cea1
- https://git.kernel.org/stable/c/a7d15eaecf0d6e13226db629ae2401c8c02683e5
- https://git.kernel.org/stable/c/edc4ef0e0154096d6c0cf5e06af6fc330dbad9d1
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21829.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21829
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
