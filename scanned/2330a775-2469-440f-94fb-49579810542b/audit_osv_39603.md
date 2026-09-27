# [H] RDMA/hns: Fix WQ_MEM_RECLAIM warning

## Summary
Severity: High
Advisory: CVE-2026-46265
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46265
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix WQ_MEM_RECLAIM warning

When sunrpc is used, if a reset triggered, our wq may lead the
following trace:

workqueue: WQ_MEM_RECLAIM xprtiod:xprt_rdma_connect_worker [rpcrdma]
is flushing !WQ_MEM_RECLAIM hns_roce_irq_workq:flush_work_handle
[hns_roce_hw_v2]
WARNING: CPU: 0 PID: 8250 at kernel/workqueue.c:2644 check_flush_dependency+0xe0/0x144
Call trace:
  check_flush_dependency+0xe0/0x144
  start_flush_work.constprop.0+0x1d0/0x2f0
  __flush_work.isra.0+0x40/0xb0
  flush_work+0x14/0x30
  hns_roce_v2_destroy_qp+0xac/0x1e0 [hns_roce_hw_v2]
  ib_destroy_qp_user+0x9c/0x2b4
  rdma_destroy_qp+0x34/0xb0
  rpcrdma_ep_destroy+0x28/0xcc [rpcrdma]
  rpcrdma_ep_put+0x74/0xb4 [rpcrdma]
  rpcrdma_xprt_disconnect+0x1d8/0x260 [rpcrdma]
  xprt_rdma_connect_worker+0xc0/0x120 [rpcrdma]
  process_one_work+0x1cc/0x4d0
  worker_thread+0x154/0x414
  kthread+0x104/0x144
  ret_from_fork+0x10/0x18

Since QP destruction frees memory, this wq should have the WQ_MEM_RECLAIM.

## References
- https://git.kernel.org/stable/c/0cbec8b49270f3f0600b8e3ef5e8f0d233dcea27
- https://git.kernel.org/stable/c/12761bd0ae16a80f237c2a65ab1b1064076cc74a
- https://git.kernel.org/stable/c/562c96b1393da2df3ea62173c84117b39da353b9
- https://git.kernel.org/stable/c/70a5eb757ace5bd627a36f04d871eaf85def424d
- https://git.kernel.org/stable/c/c0a26bbd3f99b7b03f072e3409aff4e6ec8af6f6
- https://git.kernel.org/stable/c/c5ef9a1bcf5b597695d9c2e6ac452e9f89521862
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46265.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46265
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
