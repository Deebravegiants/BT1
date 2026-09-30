# [H] RDMA/siw: Fix duplicated reported IW_CM_EVENT_CONNECT_REPLY event

## Summary
Severity: High
Advisory: CVE-2022-50136
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50136
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.211, >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Fix duplicated reported IW_CM_EVENT_CONNECT_REPLY event

If siw_recv_mpa_rr returns -EAGAIN, it means that the MPA reply hasn't
been received completely, and should not report IW_CM_EVENT_CONNECT_REPLY
in this case. This may trigger a call trace in iw_cm. A simple way to
trigger this:
 server: ib_send_lat
 client: ib_send_lat -R <server_ip>

The call trace looks like this:

 kernel BUG at drivers/infiniband/core/iwcm.c:894!
 invalid opcode: 0000 [#1] PREEMPT SMP NOPTI
 <...>
 Workqueue: iw_cm_wq cm_work_handler [iw_cm]
 Call Trace:
  <TASK>
  cm_work_handler+0x1dd/0x370 [iw_cm]
  process_one_work+0x1e2/0x3b0
  worker_thread+0x49/0x2e0
  ? rescuer_thread+0x370/0x370
  kthread+0xe5/0x110
  ? kthread_complete_and_exit+0x20/0x20
  ret_from_fork+0x1f/0x30
  </TASK>

## References
- https://git.kernel.org/stable/c/0066246d2d7e2619f3ecf3cf07333c59e6e7d84d
- https://git.kernel.org/stable/c/11edf0bba15ea9df49478affec7974f351bb2f6e
- https://git.kernel.org/stable/c/1434de50a5d9dab91c8ce031bc23b3e2178379c5
- https://git.kernel.org/stable/c/3056fc6c32e613b760422b94c7617ac9a24a4721
- https://git.kernel.org/stable/c/9ade92ddaf2347fb34298c02080caaa3cdd7c27b
- https://git.kernel.org/stable/c/f6e26e1a5f600b760dc32135d3fac846eabe09e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50136.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
